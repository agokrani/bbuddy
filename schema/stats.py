
from enum import Enum

from pydantic import BaseModel


class StatsType(str, Enum): 
    CHECK_IN_COUNTER = "CHECK_IN_COUNTER",
    REFLECRION_COUNTER = "REFLECTION_COUNTER"


class UserStats(BaseModel):
    id: int
    type: StatsType
    value: str

def user_stat_from_dict(stat): 
    return UserStats(id=stat['id'], type = StatsType(stat['type']), value=stat['value'])

def user_stat_from_tuple(stat): 
    return UserStats(id=stat[0], type=StatsType(stat[1]), value=stat[2])

def user_stats_from_list(stats): 
    return [user_stat_from_tuple(stat) for stat in stats]