"""
main.py - 힙 정렬 vs 도수 정렬 시각화 대시보드 백엔드 API
Stitch 프로젝트: projects/14863255674366848797 연동
Google Cloud Run 배포 최적화 FastAPI 애플리케이션
"""

import os
import sys
import time
import random
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from sorters import heap_sort_recorder, counting_sort_recorder, METADATA

app = FastAPI(
    title="Heap Sort vs Counting Sort Visualizer API",
    description="힙 정렬 및 도수 정렬 상태 스냅샷 데이터 제공 API (Stitch projects/14863255674366848797 연동)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

START_TIME = time.time()


class SortRequest(BaseModel):
    array: Optional[List[int]] = Field(
        default=None,
        description="정렬할 정수형 배열 (미지정 시 무작위 32개 원소 자동 생성)",
        examples=[[49, 12, 38, 25, 42, 18, 33, 48, 5, 29, 44, 15, 39, 21, 50, 8]],
    )

    @field_validator("array")
    @classmethod
    def validate_array(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        if v is not None:
            if len(v) < 3:
                raise ValueError("배열의 길이는 최소 3개 이상이어야 시각화 비교가 가능합니다.")
            if len(v) > 128:
                raise ValueError("시각화 성능을 위해 최대 128개 이하의 배열만 지원합니다.")
            if any(x < 0 for x in v):
                raise ValueError("도수 정렬(Counting Sort) 인덱싱을 위해 0 이상의 정수만 지원합니다.")
        return v


def generate_default_array(size: int = 32, max_val: int = 50) -> List[int]:
    return [random.randint(1, max_val) for _ in range(size)]


@app.get("/api/health", summary="헬스 체크")
def health_check():
    return {
        "status": "healthy",
        "service": "heep-sort-visualizer",
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "stitch_project": METADATA["project"],
    }


@app.post("/api/sort", summary="힙 정렬 및 도수 정렬 시뮬레이션 스냅샷 생성")
def generate_sort_snapshots(request_data: SortRequest):
    arr = request_data.array if request_data.array else generate_default_array(32, 50)

    start_heap = time.perf_counter()
    heap_result = heap_sort_recorder(arr)
    heap_duration_ms = round((time.perf_counter() - start_heap) * 1000, 3)

    start_counting = time.perf_counter()
    counting_result = counting_sort_recorder(arr)
    counting_duration_ms = round((time.perf_counter() - start_counting) * 1000, 3)

    heap_result["execution_time_ms"] = heap_duration_ms
    counting_result["execution_time_ms"] = counting_duration_ms

    return {
        "success": True,
        "stitch_project": METADATA["project"],
        "array_size": len(arr),
        "original_array": arr,
        "results": {
            "heap_sort": heap_result,
            "counting_sort": counting_result,
        },
        "comparison_metrics": {
            "speedup_ratio": round(heap_duration_ms / max(counting_duration_ms, 0.001), 2),
            "heap_ops": heap_result["comparisons"] + heap_result["swaps"],
            "counting_ops": counting_result["total_steps"],
        }
    }


@app.get("/api/demo", summary="내장 데모 배열 및 메타데이터 반환")
def get_demo_data():
    sample_arr = [49, 12, 38, 25, 42, 18, 33, 48, 5, 29, 44, 15, 39, 21, 50, 8, 31, 14, 46, 23, 37, 10, 27, 41, 16, 35, 20, 45, 9, 30, 43, 17]
    return {
        "success": True,
        "stitch_project": METADATA["project"],
        "sample_array": sample_arr
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)


