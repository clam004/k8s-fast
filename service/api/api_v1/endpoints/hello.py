from fastapi import APIRouter, Depends
from fastapi.security.api_key import APIKey

from service.core.models.output import MessageOutput
from service.core.models.input import MessageInput
from service.core.logic.business_logic import run_prime_factor_calculation
import service.core.auth as auth

router = APIRouter()

@router.get("/example", tags=["example get"])
def example_get():
#     """
#     Say hej!

#     This will greet you properly

#     And this path operation will:
#     * return "hej!"
#     """
    return {"msg": "Hej!"}


@router.post("/hello", response_model=MessageOutput, tags=["hello post"])
def hello_endpoint(inputs: MessageInput, api_key: APIKey = Depends(auth.get_api_key)):
    """
    Respond to requests on the hello endpoint
    """

    print(inputs)

    n, largest_prime_factor, elapsed_time = run_prime_factor_calculation()
    return {
        "default variable": api_key,
        "message1": "Hello, world!",
        "message2": f"The largest prime factor of {n} is {largest_prime_factor}. Calculation took {elapsed_time:0.3f} seconds.",
        "n": n,
        "largest_prime_factor": largest_prime_factor,
        "elapsed_time": elapsed_time,
    }