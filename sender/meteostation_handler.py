from loguru import logger

import httpx
from pydantic import BaseModel, HttpUrl
from bs4 import BeautifulSoup

from typing import Optional
from datetime import datetime


class MeteostationHandler:
    def __init__(self, address: HttpUrl):
        self.address = address

    class MeteostationData(BaseModel):
        pm25: float
        pm10: float
        temperature: float
        pressure: float
        humidity: float
        time: datetime

    async def get_current_data(self) -> Optional[str]:
        """Return text from meteostation using given adress"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.address, timeout=15.0)
            except httpx.TimeoutException:
                logger.error(f"Can't access meteostation on {self.address}.")
                return
            else:
                if response.status_code == 200:
                    return response.text

    @staticmethod
    def parse(text: str) -> MeteostationData:
        data = {}
        for row in BeautifulSoup(text,
                                 'html.parser').find('table').find_all("tr"):
            row = BeautifulSoup(row, 'html.parser').find_all('td')
            for tag in range(0, len(row)):
                row[tag] = row[tag].string  # prettify
            if len(row) == 3:
                data.update((row[1], float(row[2].split()[0])))
        return MeteostationHandler.MeteostationData(
            pm25=data['PM2.5'],
            pm10=data['PM10'],
            temperature=data['Температура'],
            pressure=data['Давление воздуха'],
            humidity=data['Относительная влажность'],
            time=datetime.now())
