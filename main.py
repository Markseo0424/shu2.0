from shu_agent import SHUAgent
from shu_manager import SHUManager

shu = SHUAgent()
with SHUManager(shu) as m:
    m.append("toolCheckUpdateNotion", {"time": {"second": 5}})
    m.append("toolCheckEvaluation", {"time": {"minute": 30}})
    m.append("calenderCheckNotion", {"every": "day", "time": {"hour": 9}})

