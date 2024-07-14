import re

from pydantic import BaseModel, Field


class HttpResponse(BaseModel):
    status_code: int
    response_message: str
    title: str
    body: str

    @property
    def html(self) -> str:
        return f"HTTP/1.1 {self.status_code} {self.response_message}\r\n\n<HTML> <HEAD> <TITLE>{self.title}</TITLE> </HEAD><BODY>{self.body}</BODY></HTML>"


BAD_REQUEST = HttpResponse(
    status_code=400, response_message="Bad Request", title="Error", body="Invalid Input"
)


def _create_days() -> dict:
    values = {}
    for day in range(1, 8):
        values[day] = dict()
        for hour in range(9, 19):
            values[day][hour] = False
    return values


class Room(BaseModel):
    name: str
    days: dict = Field(default_factory=_create_days)


class ActivityBase(BaseModel):
    name: str


class DisplayReservation(BaseModel):
    activity: str
    room: str
    day: int = Field(ge=1, le=7)
    hour: int = Field(ge=9, le=17)
    duration: int = Field(ge=1, le=9)

    @property
    def text(self) -> str:
        return f"{self.room}, {self.activity}, {self.day}, {self.hour}, {self.duration}"


class RoomBaseInput(BaseModel):
    name: str


class RoomCheckAvailabilityInput(RoomBaseInput):
    day: int = Field(ge=1, le=7)


class RoomReserveInput(RoomBaseInput):
    day: int = Field(ge=1, le=7)
    hour: int = Field(ge=9, le=17)
    duration: int = Field(ge=1, le=9)


class ReserveInput(BaseModel):
    activity: str
    room: str
    day: int = Field(ge=1, le=7)
    hour: int = Field(ge=9, le=17)
    duration: int = Field(ge=1, le=9)


class ListAvailabilityInput(BaseModel):
    room: str
    day: int = Field(None, ge=1, le=7)


class DisplayInput(BaseModel):
    id: str


class RequestResponse(BaseModel):
    header: str
    message: str

    @property
    def status_code(self) -> int:
        return int(self.header.split(" ")[1])

    @property
    def response_message(self) -> str:
        return self.header.split(" ")[2]

    @property
    def title(self) -> str:
        return re.search(r"<TITLE>(.*)<\/TITLE>", self.message).group(1)

    @property
    def body(self) -> str:
        return re.search(r"<BODY>(.*)<\/BODY>", self.message).group(1)
