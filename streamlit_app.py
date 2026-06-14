
import streamlit as st
import pandas as pd
import folium

from geopy.geocoders import Nominatim
from streamlit_folium import st_folium

from math import radians, sin, cos, sqrt, atan2

from folium.features import DivIcon
import random


# =========================
# 주소 → 좌표
# =========================

geolocator = Nominatim(
    user_agent="restaurant_recommender"
)

def geocode(address):

    try:

        location = geolocator.geocode(
            address + ", Seoul, South Korea"
        )

        if location is None:
            return None

        return (
            location.latitude,
            location.longitude
        )

    except:
        return None


# =========================
# 중심점 계산
# =========================

def get_center(coords):

    lat = sum(c[0] for c in coords) / len(coords)
    lng = sum(c[1] for c in coords) / len(coords)

    return lat, lng


# =========================
# 거리 계산(km)
# =========================

def distance(lat1, lon1, lat2, lon2):

    R = 6371

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return R * c


st.set_page_config(
    page_title="오늘 뭐 먹지?",
    page_icon="🍽️",
    layout="centered"
)

if "show_result" not in st.session_state:
    st.session_state.show_result = False

if "top5" not in st.session_state:
    st.session_state.top5 = None

if "center_lat" not in st.session_state:
    st.session_state.center_lat = None

if "center_lng" not in st.session_state:
    st.session_state.center_lng = None

if "coords" not in st.session_state:
    st.session_state.coords = None




st.markdown("""
<style>

/* 전체 영역 */
.block-container{
    max-width:850px;
    padding-top:3rem;
    padding-bottom:2rem;
}

/* 제목 */
h1{
    text-align:center;
    font-weight:700;
}

/* 설명 */
[data-testid="stCaptionContainer"]{
    text-align:center;
}

/* 입력창 */
.stTextInput input{
    border-radius:14px;
}

.stNumberInput input{
    border-radius:14px;
}

/* 버튼 */
.stButton > button{
    border-radius:14px;
    height:52px;
    font-size:18px;
    font-weight:600;
}

/* 여백 축소 */
hr{
    margin-top:0.8rem;
    margin-bottom:0.8rem;
}

/* toggle 전체 */

[data-testid="stToggle"]{
    border:1px solid #e5e5e5;
    border-radius:16px;
    padding:14px;
    margin-bottom:10px;
    background:white;
    transition:0.2s;
}

/* hover */

[data-testid="stToggle"]:hover{
    box-shadow:0 2px 10px rgba(0,0,0,0.08);
}

/* label */

[data-testid="stToggle"] label{
    font-size:18px;
    font-weight:600;
}

/* 부제목 */
h3{
    text-align:center;
}

/* 본문 */
.center-text{
    text-align:center;
}

</style>
""", unsafe_allow_html=True)

# =========================
# 사이드바
# =========================

page = st.sidebar.radio(
    "메뉴",
    ["웹앱 개요", "음식 추천"]
)

# =========================
# 랜딩 페이지
# =========================

if page == "웹앱 개요":

    st.title("🍽️ 오늘 뭐 먹지?")

    st.caption(

        "위치와 취향을 기반으로 최적의 식당을 추천해드립니다."
    )

    st.markdown("---")

    st.subheader("웹 앱 소개")

    st.markdown(
        """
        <div class="center-text">
        혼자 먹을 식당을 고르거나 누군가와의 약속장소를 고를 때,<br>
        수많은 식당을 보며 고민하는 사람들을 위한 음식점 추천 앱!<br>
        (현재까지는 서울 지역만 구현됨)
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.subheader("사용법")

    st.markdown("""

    0. **사이드 바의 '음식추천' 탭 클릭**  

    1. **인원수 입력**        
            
    2. **각 인원의 현재 위치 입력**  
       (도로명주소로 입력해 주시고, 상세주소는 입력하지 마세요!)  
       (예시: 서울 서초구 효령로 347 🥰  |   서울 서초구 효령로 347 *서광빌딩 1층* 😩)  
       (인원이 여러명이지만 위치는 하나인 경우, 인원수 1명 선택 후 위치 하나만 적어주세요!)  
       (입력된 위치를 계산하여 위치가 여럿일 경우 각 위치의 중점을 기준으로 음식점을 추천하고 있습니다)  
            
    3. **선호/비선호 음식 선택** (체크박스 클릭 시 선택 가능, 다시 클릭하면 해제 가능, 중복선택 가능)   
                 
    4. **식사 목적 선택** (마찬가지로 클릭해서 선택/해제 가능, 중복선택 가능)     
              
    5. **추천받기 버튼 클릭!**    
                     
    6. **추천 탭 살펴보기!** (🔵사용자위치 💚중심위치 🔴음식점위치, 지도 위 마커 클릭 시 해당 음식점의 정보 확인 가능)  
       (streamlit에서 사용할 수 있는 위치변환 시스템의 한계로 정확한 위치 표시가 어렵습니다. 현재 위치보다 조금 떨어진 곳에 사용자 위치가 표시될 수 있습니다.)     

    7. **랜덤 추천 받기**  (제외하고 싶은 후보군을 클릭해 제외한 후 랜덤 추천 받기, 재추첨 가능)

    """)

    st.markdown("---")

    st.subheader("웹 앱 원리 설명")

    st.markdown("""

    1. **데이터 수집/가공**  
    - 서울 열린데이터 광장 지하철역 정보 csv와 카카오 API를 이용하여, 서울시의 지하철 역 주변에 위치한 음식점 정보 수집
    - 수집한 음식점 이름을 통한 블로그 검색결과 크롤링으로 해당 음식점의 리뷰 수집
    - 리뷰 (블로그 게시물 제목과 글 내용 미리보기)의 단어 빈도수를 분석해 해당 음식점의 카테고리/분위기 파악
    - 수집한 정보를 csv형태로 최종 저장  
      (컬럼: 도로명주소, 음식점카테고리(한식, 일식, 중식 등), 음식점 상호명, 카카오맵 상세페이지 주소, 경도, 위도, 분석한 분위기/카테고리 태그)   
            
    2. **추천 음식점 계산 로직**  
    ```python
    # 선호 음식
    for food in preferred_foods:
        candidate_df.loc[
            candidate_df["category_name"]
            .str.contains(food, na=False),
            "score"
        ] += 20

    # 비선호 음식
    for food in disliked_foods:
        candidate_df.loc[
            candidate_df["category_name"]
            .str.contains(food, na=False),
            "score"
        ] -= 60

    # 식사 목적
    for mood in selected_moods:
        candidate_df.loc[
            candidate_df["tags"]
            .fillna("")
            .str.contains(mood),
            "score"
        ] += 25

    # 거리
    candidate_df["score"] += (
        (1 - candidate_df["distance"])
        * 30
    )
    ```
    - 선호 음식 카테고리 하나당 +20
    - 비선호 음식 카테고리 하나당 -60
    - 식사 목적 하나당 +25
    - 거리가 가까울수록 최대 +30  
    - 점수를 전부 합해서 가장 높은 5개의 음식점을 지도에 표시  

    3. **랜덤 추천 로직**  
    ```python
    st.session_state.random_result = available_df.sample(1).iloc[0]
    ```
    - 위 코드를 이용하여 후보군 중에서 랜덤 선택

    """)

# =========================
# 음식 추천 페이지
# =========================

elif page == "음식 추천":

    st.title("🍽️ 오늘 뭐 먹지?")

    st.caption(

        "위치와 취향을 기반으로 최적의 식당을 추천해드립니다."
    )

    st.markdown("---")

    if "excluded_places" not in st.session_state:
        st.session_state.excluded_places = []

    if "random_result" not in st.session_state:
        st.session_state.random_result = None

    if "failed_locations" not in st.session_state:
        st.session_state.failed_locations = []

    # =========================
    # 인원수 + 위치
    # =========================

    left, center, right = st.columns([1,4,1])

    with center:

        col1, col2 = st.columns([1, 3])

        with col1:

            people = st.number_input(
                "인원수",
                min_value=1,
                value=2,
                step=1
            )

        with col2:

            locations = []

            for i in range(people):

                loc = st.text_input(
                    f"{i+1}번 위치",
                    placeholder="도로명 주소를 입력하고 엔터를 눌러주세요",
                    key=f"loc_{i}"
                )

                locations.append(loc)

        st.markdown("---")

        # =========================
        # 음식 카테고리
        # =========================

        preferred_foods = st.pills(
            "🍜 선호 음식",
            [
                "한식",
                "중식",
                "일식",
                "양식",
                "분식",
                "치킨",
                "피자",
                "고기",
                "해산물",
                "카페"
            ],
            selection_mode="multi"
        )

        disliked_foods = st.pills(
            "😩 비선호 음식",
            [
                "한식",
                "중식",
                "일식",
                "양식",
                "분식",
                "치킨",
                "피자",
                "고기",
                "해산물",
                "카페"
            ],
            selection_mode="multi"
        )

        st.markdown("---")

        # =========================
        # 식사목적
        # =========================

        col1, col2 = st.columns(2)

        with col1:
            mood_date = st.toggle("💕 데이트")
            mood_family = st.toggle("👨‍👩‍👧 가족외식")
            mood_friend = st.toggle("😋 친구모임")
            mood_waiting = st.toggle("🔥 웨이팅맛집")
            mood_tour = st.toggle("📸 관광맛집")

        with col2:
            mood_solo = st.toggle("🍚 혼밥")
            mood_meeting = st.toggle("🍻 회식")
            mood_infinite = st.toggle("🍽️ 무한리필, 뷔페")
            mood_value = st.toggle("💰 가성비")
            mood_parking = st.toggle("🚗 주차가능")

        st.markdown("---")

        if st.button(
            "🍽️ 추천받기",
            use_container_width=True
        ):
            st.session_state.show_result = True

            st.session_state.top5 = None
            st.session_state.center_lat = None
            st.session_state.center_lng = None
            st.session_state.coords = None

    st.markdown("---")

    st.subheader("📍 추천 결과")

    if st.session_state.show_result and st.session_state.failed_locations:

        failed_text = ", ".join(st.session_state.failed_locations)

        st.error(f"❌ 다음 위치를 찾을 수 없습니다. 다시 입력해주세요: {failed_text}")

    if st.session_state.show_result:

        if st.session_state.top5 is None:

            try:

                # =========================
                # 위치 변환
                # =========================

                coords = []
                st.session_state.failed_locations = []

                for location in locations:

                    location = location.strip()

                    if not location:
                        continue

                    result = geocode(location)

                    if not result:
                        st.session_state.failed_locations.append(location)
                        continue

                    lat, lng = result

                    # =========================
                    # 🔥 핵심: "서울 중심 기준 거리 체크"
                    # =========================

                    SEOUL_CENTER = (37.5665, 126.9780)

                    d = distance(
                        SEOUL_CENTER[0],
                        SEOUL_CENTER[1],
                        lat,
                        lng
                    )

                    # 👉 너무 멀면 이상값 처리 (예: 50km 이상이면 reject)
                    if d > 50:
                        st.session_state.failed_locations.append(location)
                        continue

                    coords.append((lat, lng))

                # =========================
                # 중심점 계산
                # =========================

                center_lat, center_lng = get_center(coords)

                # =========================
                # CSV 읽기
                # =========================

                restaurant_df = pd.read_csv(
                    "restaurants_final.csv",
                    encoding="utf-8-sig"
                )

                restaurant_df["x"] = restaurant_df["x"].astype(float)
                restaurant_df["y"] = restaurant_df["y"].astype(float)

                # =========================
                # 거리 계산
                # =========================

                restaurant_df["distance"] = restaurant_df.apply(
                    lambda row:
                    distance(
                        center_lat,
                        center_lng,
                        row["y"],
                        row["x"]
                    ),
                    axis=1
                )

                # =========================
                # 1km 필터
                # =========================

                candidate_df = restaurant_df[
                    restaurant_df["distance"] <= 1
                ].copy()

                if len(candidate_df) == 0:

                    st.warning(
                        "1km 내에 추천 가능한 음식점이 없습니다."
                    )

                    st.stop()

                # =========================
                # 점수
                # =========================

                candidate_df["score"] = 0

                # 음식 선호

                for food in preferred_foods:

                    candidate_df.loc[
                        candidate_df["category_name"]
                        .str.contains(food, na=False),
                        "score"
                    ] += 20

                # 음식 비선호

                for food in disliked_foods:

                    candidate_df.loc[
                        candidate_df["category_name"]
                        .str.contains(food, na=False),
                        "score"
                    ] -= 60

                # 식사목적 선택

                selected_moods = []

                if mood_date:
                    selected_moods.append("데이트")

                if mood_family:
                    selected_moods.append("가족외식")

                if mood_waiting:
                    selected_moods.append("웨이팅맛집")

                if mood_tour:
                    selected_moods.append("관광맛집")

                if mood_solo:
                    selected_moods.append("혼밥")

                if mood_meeting:
                    selected_moods.append("회식")

                if mood_value:
                    selected_moods.append("가성비")

                if mood_parking:
                    selected_moods.append("주차가능")

                if mood_friend:
                    selected_moods.append("친구모임")

                if mood_infinite:
                    selected_moods.append("무한리필, 뷔페")

                for mood in selected_moods:

                    candidate_df.loc[
                        candidate_df["tags"]
                        .fillna("")
                        .str.contains(mood),
                        "score"
                    ] += 25

                # 거리 가까울수록 보너스

                candidate_df["score"] += (
                    (1 - candidate_df["distance"])
                    * 30
                )

                # =========================
                # TOP 5
                # =========================

                top5 = candidate_df.sort_values(
                    ["score", "distance"],
                    ascending=[False, True]
                ).head(5)

                st.session_state.top5 = top5
                st.session_state.random_candidates = top5.copy()
                st.session_state.random_result = None

                st.session_state.center_lat = center_lat
                st.session_state.center_lng = center_lng
                st.session_state.coords = coords

            except Exception as e:

                st.exception(e)

            st.markdown("---")

        if st.session_state.top5 is not None:

            m = folium.Map(
                location=[
                    st.session_state.center_lat,
                    st.session_state.center_lng
                ],
                zoom_start=15,
                tiles="CartoDB positron"
            )

            # 사용자 위치

            for idx, (lat, lng) in enumerate(st.session_state.coords, start=1):

                folium.Marker(
                    [lat, lng],
                    icon=DivIcon(
                        html=f"""
                        <div style="
                            background:#4285F4;
                            width:24px;
                            height:24px;
                            border-radius:50%;
                            text-align:center;
                            line-height:24px;
                            color:white;
                            font-weight:bold;
                        ">
                        {idx}
                        </div>
                        """
                    ),
                    tooltip=f"{idx}번 사용자"
                ).add_to(m)

            # 중심점

            if len(st.session_state.coords) >= 2:

                folium.Marker(
                    [
                        st.session_state.center_lat,
                        st.session_state.center_lng
                    ],
                    icon=DivIcon(
                        html="""
                        <div style="
                            background:#34A853;
                            width:24px;
                            height:24px;
                            border-radius:50%;
                            text-align:center;
                            line-height:24px;
                            color:white;
                            font-weight:bold;
                        ">
                        ⭐
                        </div>
                        """
                    ),
                    tooltip="중간 지점"
                ).add_to(m)

            # 음식점

            for _, row in st.session_state.top5.iterrows():

                popup_html = f"""
                <div style="width:250px">
                    <h4 style="margin-top: 20px">🍽 {row['place_name']}</h4>
                    <p style="margin-bottom: -17px">📍 {row['address_name']}</p>
                    <p style="margin-bottom: -17px">🍽️ {row['category_name']}</p>
                    <p>✨ {row['tags']}</p>
                    <a href="{row['place_url']}" target="_blank">
                    카카오맵 보기
                    </a>
                </div>
                """

                folium.Marker(
                    location=[row["y"], row["x"]],
                    icon=DivIcon(
                        html="""
                        <div style="
                            background:#ff4b4b;
                            width:24px;
                            height:24px;
                            border-radius:50%;
                            text-align:center;
                            line-height:24px;
                            color:white;
                            font-weight:bold;
                        ">
                        🍽️
                        </div>
                        """
                    ),
                    tooltip=row['place_name'],
                    popup=popup_html
                ).add_to(m)

            st_folium(
                m,
                width=800,
                height=500
            )


        st.markdown("### 🍽 추천 음식점")

        for _, row in st.session_state.top5.iterrows():

            st.markdown(
                f"""
                **{row['place_name']}**

                - 주소: {row['address_name']}
                - 카테고리: {row['category_name']}
                - 태그: {row['tags']}
                """
            )
            st.link_button(
                "카카오맵에서 보기",
                row["place_url"]
            )
            st.markdown("---")

        st.markdown("## 🎲 랜덤 추첨")

        top5_names = st.session_state.top5["place_name"].tolist()

        # =========================
        # ❌ 제외 (pills 방식)
        # =========================
        excluded_places = st.pills(
            "❌ 제외할 음식점 선택",
            top5_names,
            selection_mode="multi"
        )

        # =========================
        # 남은 후보 계산
        # =========================
        available_df = st.session_state.top5[
            ~st.session_state.top5["place_name"].isin(excluded_places)
        ].copy()

        st.markdown("### 남은 후보")

        if len(available_df) == 0:
            st.warning("남은 후보가 없습니다.")
        else:
            for name in available_df["place_name"]:
                st.write("•", name)

        # =========================
        # 랜덤 결과 초기화 안전 처리
        # =========================
        if "random_result" not in st.session_state:
            st.session_state.random_result = None

        # =========================
        # 버튼 영역
        # =========================

        if st.button("🎲 랜덤 추천받기"):

            if len(available_df) == 0:
                st.warning("추천할 음식점이 없습니다.")
            else:
                st.session_state.random_result = available_df.sample(1).iloc[0]     

        # =========================
        # 결과 출력
        # =========================
        if st.session_state.random_result is not None:

            row = st.session_state.random_result

            # 현재 available_df 기준으로 유효성 체크 (중요)
            if row["place_name"] not in available_df["place_name"].values:
                st.session_state.random_result = None
                st.warning("현재 제외 설정 때문에 결과가 초기화되었습니다.")
            else:

                st.success(f"🎉 오늘의 추천: {row['place_name']}")

                st.markdown(f"""
                **{row['place_name']}**

                - 주소: {row['address_name']}
                - 카테고리: {row['category_name']}
                - 태그: {row['tags']}
                """)

                st.link_button(
                    "카카오맵 보기",
                    row["place_url"]
                )
