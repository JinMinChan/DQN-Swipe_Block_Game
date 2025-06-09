# DQN - Swipe Block Game

본 프로젝트는 강화학습(Deep Reinforcement Learning) 알고리즘인 \*\*DQN(Deep Q-Network)\*\*을 이용하여, Pygame으로 제작한 "스와이프 벽돌깨기" 게임을 학습하는 환경을 구축하고 에이전트가 효율적인 전략을 학습하도록 구성한 프로젝트입니다.

## 개발 환경

* **운영체제**: Windows 11
* **Python 버전**: Python 3.9.21 (Anaconda 가상환경)

### 필수 패키지

```
gym==0.26.2
stable-baselines3==2.6.0
pygame==2.6.1
numpy==2.0.2
pandas==2.2.3
matplotlib==3.9.4
shimmy==2.0.0
torch==2.7.0
```

### 설치 방법

Anaconda 환경에서 아래 명령어로 설치합니다:

```bash
pip install gym stable-baselines3 pygame numpy pandas matplotlib shimmy
```

## 게임 및 환경 개요

본 프로젝트는 직접 제작한 스와이프 벽돌깨기 게임을 OpenAI Gym 형태로 래핑하여 강화학습 환경으로 제공하며, 에이전트는 공의 발사 각도를 선택해 벽돌을 효율적으로 제거하는 전략을 학습합니다.

### 게임 규칙

* 공의 발사 각도를 설정하여 벽돌을 공격합니다.
* 벽돌에 공이 닿으면 체력이 1 감소하며, 체력이 0이 되면 벽돌은 사라집니다.
* 보너스 공을 획득할 때마다 공의 수가 증가합니다.
* 모든 공이 바닥에 닿으면 턴이 종료되고 새로운 블록 행이 추가됩니다.
* 벽돌이 화면 최하단(8번째 줄)에 도달하면 게임이 종료됩니다.

## 상태(State) 및 행동(Action) 정의

### State

* 블록 체력 분포 (정규화된 2차원 배열)
* 보너스 공의 위치 (정규화된 2차원 배열)
* 공의 발사 위치 x 좌표 (정규화된 값)
* 보유 공의 개수 (정규화된 값)

### Action

* 공을 발사할 각도를 나타내며, 21개의 이산 각도 중 하나를 선택합니다.

### Reward

* 한 턴 동안 감소한 블록 체력 비율을 기반으로 보상을 부여합니다.
* 게임 실패 시 명확한 패널티(-1)를 제공합니다.

## 강화학습 알고리즘 (DQN)

본 프로젝트는 stable-baselines3를 사용하여 DQN 알고리즘을 구현하였으며, 다음의 기법들이 적용되었습니다:

* **Experience Replay**: 과거 경험을 무작위로 샘플링하여 데이터 효율성과 학습 안정성을 높임
* **Target Network**: 주기적인 네트워크 업데이트로 안정적인 학습 진행

### 사용된 주요 하이퍼파라미터

* learning\_rate: 0.0003
* buffer\_size: 100,000
* batch\_size: 256
* gamma: 0.99
* exploration\_fraction: 0.40
* exploration\_final\_eps: 0.1
* target\_update\_interval: 1
* tau: 0.005

## 학습 결과 시각화

* 학습 중 성능 지표(보상, 에피소드 길이, 손실, 탐색률)를 그래프로 시각화하여 저장하였습니다.
* 가장 좋은 성능의 모델을 저장하여 최종 평가를 수행합니다.

## 결과 데모 영상

(https://drive.google.com/file/d/1tEKB3N37gExijq9tUg-2yqusiKLWLKdx/view?usp=sharing)
