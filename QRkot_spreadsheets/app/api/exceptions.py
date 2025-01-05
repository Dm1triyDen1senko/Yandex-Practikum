from fastapi import HTTPException, status


class BadRequestException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail
        )


class UnproccesableEntityException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail
        )


class NotFoundException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail=detail
        )
