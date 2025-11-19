"""股票筛选 API 路由"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.screener import ScreenerRequest, ScreenerResponse, ScreenerResult
from app.services.screener_service import ScreenerService

router = APIRouter()


@router.post("/screen", response_model=ScreenerResponse)
async def screen_stocks(
    request: ScreenerRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    股票筛选

    支持的筛选字段:
    - current_price: 当前价格
    - change_percent: 涨跌幅
    - volume: 成交量
    - market_cap: 市值
    - pe_ratio: 市盈率
    - pb_ratio: 市净率
    - roe: 净资产收益率
    - roa: 总资产收益率
    - gross_margin: 毛利率
    - net_margin: 净利率
    - revenue_growth: 营收增长率
    - debt_to_equity: 资产负债率

    支持的运算符:
    - gt: 大于
    - gte: 大于等于
    - lt: 小于
    - lte: 小于等于
    - eq: 等于
    - ne: 不等于
    - between: 区间 (value 为 [min, max])
    - in: 包含于 (value 为列表)

    示例请求:
    ```json
    {
        "market": "CN",
        "conditions": [
            {"field": "pe_ratio", "operator": "between", "value": [10, 20]},
            {"field": "roe", "operator": "gte", "value": 0.15}
        ],
        "order_by": "roe",
        "order_direction": "desc",
        "limit": 50
    }
    ```

    Returns:
        筛选结果列表和总数
    """
    results, total = await ScreenerService.screen_stocks(db, request)

    return ScreenerResponse(
        total=total,
        results=[ScreenerResult(**r) for r in results],
        conditions=request.conditions,
    )


@router.get("/fields")
async def get_available_fields():
    """
    获取可用的筛选字段、运算符和市场列表

    Returns:
        字段定义、运算符列表、市场列表
    """
    return await ScreenerService.get_available_fields()
