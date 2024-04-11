import fastapi
import uvicorn

app = fastapi.FastAPI()


class Test:
    ...


# Dependency
def get_db():
    try:
        yield Test()
    finally:
        print("finally")


router = fastapi.APIRouter()


class ItemCBV:
    @router.get("/")
    def f(self, test=fastapi.Depends(get_db)):
        print(id(test))
        print("hey")

    @router.post("/")
    def g(self, test=fastapi.Depends(get_db)):
        print(id(test))
        print("hey")


app.include_router(router)

uvicorn.run(app=app, port=5000)
