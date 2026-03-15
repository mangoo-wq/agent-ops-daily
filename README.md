# Agent Ops Daily

업데이트: 2026-03-15 (KST)
상태: v1 scaffold
성격: **저비용 · 저개입 · 무서버 지향 트래픽형 부업**

## 1) 이 프로젝트가 하는 일
Moltbook 같은 agent-native 커뮤니티에서 반복적으로 나오는 신호를 수집해서,
정적 사이트와 외부 채널(X 등)에 재가공 가능한 **Agent Ops 미디어 자산**으로 쌓는다.

핵심 질문:
- 요즘 에이전트들은 어디서 신뢰를 잃는가?
- 어떤 metric이 반복 등장하는가?
- 어떤 운영 패턴이 뜨는가?
- 어떤 실패 사례가 상품화 가능한 신호를 주는가?

## 2) 왜 이 방식인가
사장님 선호는 명확하다:
- 사람 많이 붙는 사업 ❌
- 서버비/운영비 큰 SaaS ❌
- 자동사냥처럼 저개입·무개입 수익 구조 ✅

그래서 v1은 **SaaS가 아니라 트래픽 자산 축적 모델**로 간다.

## 3) v1 원칙
1. **No server first**
   - GitHub Pages + GitHub Actions 기반
2. **Traffic first**
   - 광고/스폰서/제휴 수익화 가능성에 집중
3. **Source-first**
   - Moltbook는 신호원 / 소재 채굴장으로 활용
4. **Approval before public writes**
   - 공개 포스팅/X 자동 발행은 사장님 승인 전까지 연결하지 않음
5. **Archive compounds**
   - 하루치 요약이 쌓여 SEO/검색 자산이 되게 설계

## 4) v1 스택
- Source: Moltbook API (read-only)
- Build: Python script
- Storage: Git repo
- Publish: GitHub Pages (향후)
- Scheduler: GitHub Actions (향후 수동 → 반자동 → 자동)
- Distribution: X 티저 / 링크 공유 (승인 후)

## 5) v1 산출물
- Daily Signals page
- Theme archive (interrupt / authority / evaluation)
- Metric watchlist
- Featured threads list
- Weekly recap 초안

## 6) 수익화 순서
### Stage 1 — Traffic
- 검색 유입
- X 링크 유입
- 커뮤니티 공유 유입

### Stage 2 — Monetization
- 스폰서 슬롯
- 툴/서비스 제휴 링크
- 디렉토리 featured placement

### Stage 3 — Optional premium
- 월간 리포트
- curated dataset
- operator playbook bundle

## 7) 지금 당장 안 하는 것
- 사람 맞춤 컨설팅
- 맞춤 대행
- 고정적인 1:1 운영 지원
- 서버 상시 운영이 필요한 API 사업

## 8) 다음 단계
1. Moltbook 신호 자동 수집 스크립트 로컬 검증
2. 정적 페이지 초안 자동 생성
3. GitHub Actions로 수동 실행 가능하게 구성
4. 사이트명/도메인/브랜딩 확정
5. public launch 승인 후 GitHub Pages + X 배포 연결
