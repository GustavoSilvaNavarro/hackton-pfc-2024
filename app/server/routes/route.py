from fastapi import APIRouter, status
from app.services import find_constrain_data
router = APIRouter()


@router.get(
    "/constraint/{pfid}", tags=["Constraint"], description="Find an acs that it is under constraint or not", status_code=status.HTTP_200_OK
)
async def find_constraint(pfid: str):
    """It should find a site that is in constraint."""
    acn_id, acc_id, acg_id, acs_id = pfid.split("-")
    query = await find_constrain_data(acn=acn_id, acc=acc_id, acg=acg_id, acs=acs_id)
    print(query)
    return {"msg": "Hello"}
