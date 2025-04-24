from typing import Annotated
from fastapi import Depends, Request, HTTPException, status

from app.apis.retailcrm import (
    RetailCRM_API,
    RequestFailedException,
    ServiceTemporaryUnavailableException,
    InvalidInputException,
    BaseRetailCRMAPIException,
)


async def get_retailcrm_api_client(request: Request):
    try:
        yield request.app.state.retailCRM_api_client
    except ServiceTemporaryUnavailableException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Сервис временно не доступен",
        )
    except InvalidInputException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RequestFailedException as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
    except BaseRetailCRMAPIException:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY)
    except:
        raise


RetailCRM_API_Client_Dep = Annotated[RetailCRM_API, Depends(get_retailcrm_api_client)]
