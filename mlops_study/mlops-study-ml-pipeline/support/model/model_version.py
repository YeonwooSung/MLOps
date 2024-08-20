from support.model.repository.model_version_repository import (
    ModelVersionRepository
)


class ModelVersion:
    DEFAULT_REPOSITORY = ModelVersionRepository()

    def __init__(self,
                 model_name: str,
                 repository=DEFAULT_REPOSITORY):
        self._model_name = model_name
        self._repository = repository

    def get_final_ct_model_version(self):
        return self._repository. \
            get_final_ct_model_version(model_name=self._model_name)

    def get_next_ct_model_version(self):
        """ 지속적학습(CT) 모델 다음 버전을 조회 한다. """

        # 현재 모델 버전을 조회 한다.
        final_ct_model_version = self.get_final_ct_model_version()
        if final_ct_model_version is None:  # 모델 버전 미존재 시
            return "1.0.0"

        # 모델 버전을 major, minor, build 으로 분리 한다.
        model_version = final_ct_model_version.split(".")
        major = model_version[0]
        minor = model_version[1]
        build = int(model_version[2])

        # build 버전을 1 증가 시킨다.
        build += 1

        # CT 모델버전을 조립 한다.
        next_ct_model_version = ".".join([major, minor, str(build)])
        return next_ct_model_version
