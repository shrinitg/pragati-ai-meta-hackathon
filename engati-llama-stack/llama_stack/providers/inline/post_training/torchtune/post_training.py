# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.
from datetime import datetime
from typing import Any, Dict, Optional

from llama_models.schema_utils import webmethod

from llama_stack.apis.datasetio import DatasetIO
from llama_stack.apis.datasets import Datasets
from llama_stack.apis.post_training import (
    AlgorithmConfig,
    DPOAlignmentConfig,
    JobStatus,
    ListPostTrainingJobsResponse,
    LoraFinetuningConfig,
    PostTrainingJob,
    PostTrainingJobArtifactsResponse,
    PostTrainingJobStatusResponse,
    TrainingConfig,
)
from llama_stack.providers.inline.post_training.torchtune.config import (
    TorchtunePostTrainingConfig,
)
from llama_stack.providers.inline.post_training.torchtune.recipes.lora_finetuning_single_device import (
    LoraFinetuningSingleDevice,
)


class TorchtunePostTrainingImpl:
    def __init__(
        self,
        config: TorchtunePostTrainingConfig,
        datasetio_api: DatasetIO,
        datasets: Datasets,
    ) -> None:
        self.config = config
        self.datasetio_api = datasetio_api
        self.datasets_api = datasets

        # TODO: assume sync job, will need jobs API for async scheduling
        self.jobs_status = {}
        self.jobs_list = []
        self.checkpoints_dict = {}

    async def supervised_fine_tune(
        self,
        job_uuid: str,
        training_config: TrainingConfig,
        hyperparam_search_config: Dict[str, Any],
        logger_config: Dict[str, Any],
        model: str,
        checkpoint_dir: Optional[str],
        algorithm_config: Optional[AlgorithmConfig],
    ) -> PostTrainingJob:
        for job in self.jobs_list:
            if job_uuid == job.job_uuid:
                raise ValueError(f"Job {job_uuid} already exists")

        post_training_job = PostTrainingJob(job_uuid=job_uuid)

        job_status_response = PostTrainingJobStatusResponse(
            job_uuid=job_uuid,
            status=JobStatus.scheduled,
            scheduled_at=datetime.now(),
        )

        self.jobs_list.append(post_training_job)
        if isinstance(algorithm_config, LoraFinetuningConfig):
            try:
                recipe = LoraFinetuningSingleDevice(
                    self.config,
                    job_uuid,
                    training_config,
                    hyperparam_search_config,
                    logger_config,
                    model,
                    checkpoint_dir,
                    algorithm_config,
                    self.datasetio_api,
                    self.datasets_api,
                )

                job_status_response.status = JobStatus.in_progress
                job_status_response.started_at = datetime.now()

                await recipe.setup()
                resources_allocated, checkpoints = await recipe.train()

                self.checkpoints_dict[job_uuid] = checkpoints
                job_status_response.resources_allocated = resources_allocated
                job_status_response.checkpoints = checkpoints
                job_status_response.status = JobStatus.completed
                job_status_response.completed_at = datetime.now()

            except Exception:
                job_status_response.status = JobStatus.failed
                raise
        else:
            raise NotImplementedError()

        self.jobs_status[job_uuid] = job_status_response

        return post_training_job

    async def preference_optimize(
        self,
        job_uuid: str,
        finetuned_model: str,
        algorithm_config: DPOAlignmentConfig,
        training_config: TrainingConfig,
        hyperparam_search_config: Dict[str, Any],
        logger_config: Dict[str, Any],
    ) -> PostTrainingJob: ...

    async def get_training_jobs(self) -> ListPostTrainingJobsResponse:
        return ListPostTrainingJobsResponse(data=self.jobs_list)

    @webmethod(route="/post-training/job/status")
    async def get_training_job_status(
        self, job_uuid: str
    ) -> Optional[PostTrainingJobStatusResponse]:
        if job_uuid in self.jobs_status:
            return self.jobs_status[job_uuid]
        return None

    @webmethod(route="/post-training/job/cancel")
    async def cancel_training_job(self, job_uuid: str) -> None:
        raise NotImplementedError("Job cancel is not implemented yet")

    @webmethod(route="/post-training/job/artifacts")
    async def get_training_job_artifacts(
        self, job_uuid: str
    ) -> Optional[PostTrainingJobArtifactsResponse]:
        if job_uuid in self.checkpoints_dict:
            checkpoints = self.checkpoints_dict.get(job_uuid, [])
            return PostTrainingJobArtifactsResponse(
                job_uuid=job_uuid, checkpoints=checkpoints
            )
        return None
