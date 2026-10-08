from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# CORS 설정: 구글 앱스 스크립트 도메인과의 Cross-Origin 요청을 허용합니다.
CORS(app)

@app.route('/', methods=['GET'])
def health_check():
    """서버 동작 상태 확인용 헬스체크 엔드포인트"""
    return jsonify({
        "status": "online",
        "message": "Google Cloud Run Linear Search Server is running."
    }), 200

@app.route('/search', methods=['POST'])
def linear_search():
    """
    선형검색 알고리즘을 수행하고, 각 단계별 비교 상태와 결과를 반환하는 엔드포인트
    
    [Request Body]
    {
        "array": [10, 20, 30, 40, 50],
        "target": 30
    }
    """
    try:
        data = request.get_json()
        
        # 입력 값 유효성 검사
        if not data or 'array' not in data or 'target' not in data:
            return jsonify({
                "error": "잘못된 요청 형식입니다. 'array'와 'target' 필드가 필요합니다."
            }), 400
            
        array = data['array']
        target = data['target']
        
        # 선형검색 실행 및 단계별 로깅
        steps = []
        found_index = -1
        
        for index, value in enumerate(array):
            is_match = (value == target)
            steps.append({
                "step": index + 1,
                "index": index,
                "current_value": value,
                "target": target,
                "is_match": is_match,
                "description": f"인덱스 {index}의 값 {value}와(과) 타겟 {target} 비교 -> {'일치' if is_match else '불일치'}"
            })
            
            if is_match:
                found_index = index
                break  # 타겟을 찾으면 검색 종료
                
        # 최종 응답 구조 생성 (복잡도 분석 포함)
        response = {
            "status": "success",
            "input_array": array,
            "target": target,
            "found_index": found_index,
            "is_found": found_index != -1,
            "total_steps": len(steps),
            "steps": steps,
            "complexity": {
                "time_complexity": {
                    "best": "O(1) - 첫 번째 요소에서 탐색 성공",
                    "average": "O(N) - 평균적으로 N/2회 비교",
                    "worst": "O(N) - 배열 전체 탐색 또는 타겟 없음"
                },
                "space_complexity": "O(1) - 보조 메모리 사용 없음 (단계 로깅 제외 기준)"
            }
        }
        
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Cloud Run은 PORT 환경변수를 제공하므로 이를 수신하도록 설정합니다.
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
