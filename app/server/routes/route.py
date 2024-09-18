from fastapi import APIRouter, status
from app.services import find_constrain_data
router = APIRouter()


@router.get(
    "/constraint/{acn_id}/acc/{acc_id}", tags=["Constraint"], description="Find a site that it is under constraint", status_code=status.HTTP_200_OK
)
async def find_constraint(acn_id: str, acc_id: str):
    """It should find a site that is in constraint."""
    query = await find_constrain_data(acn=acn_id, acc=acc_id)
    print(query)
    return {"msg": "Hello"}
