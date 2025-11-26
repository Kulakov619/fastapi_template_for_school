import datetime
from schemas.examples import ExampleResponse, ExampleBase
from utils.encode import encode_base64


class ExamplesService:

    async def get_example(self, data: str) -> ExampleResponse:
        ex1 = ExampleBase(
            type="input",
            time=datetime.datetime.now(),
            code=data
        )
        data = await encode_base64(data)
        ex2 = ExampleBase(
            type="output",
            time=datetime.datetime.now(),
            code=data
        )
        result = [ex1, ex2]
        response = ExampleResponse(
            data=result
        )
        return response
