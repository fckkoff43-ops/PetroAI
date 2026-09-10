import streamlit as st
import pandas as pd
import plotly.express as px

from io import BytesIO
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak
)

# =========================
# KONFIGURASI HALAMAN
# =========================

st.set_page_config(
    page_title="PetroAI Analyzer",
    page_icon="🛢️",
    layout="wide"
)

# =========================
# HEADER
# =========================

st.title("🛢️ PetroAI Analyzer")
st.subheader("Petroleum Production Expert System")

st.write(
    "Sistem analisis data produksi sumur untuk mengevaluasi "
    "Water Cut, WOR, dan performa produksi."
)

st.divider()

# =========================
# UPLOAD FILE
# =========================

st.write("### 📁 Upload Production Data")

uploaded_file = st.file_uploader(
    "Upload file Excel atau CSV",
    type=["xlsx", "csv"]
)

if uploaded_file is not None:

    try:

        # =========================
        # BACA FILE
        # =========================

        if uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)

        st.success("✅ File berhasil dibaca!")

        # =========================
        # CEK KOLOM
        # =========================

        required_columns = [
            "Date",
            "Oil Rate",
            "Water Rate"
        ]

        missing_columns = [
            col for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:

            st.error(
                "❌ Kolom berikut belum ditemukan: "
                + ", ".join(missing_columns)
            )

            st.info(
                "Format kolom yang diperlukan: "
                "Date, Oil Rate, Water Rate"
            )

        else:

            # =========================
            # DATA PROCESSING
            # =========================

            df["Date"] = pd.to_datetime(
                df["Date"],
                errors="coerce"
            )

            df["Oil Rate"] = pd.to_numeric(
                df["Oil Rate"],
                errors="coerce"
            )

            df["Water Rate"] = pd.to_numeric(
                df["Water Rate"],
                errors="coerce"
            )

            df = df.dropna(
                subset=[
                    "Date",
                    "Oil Rate",
                    "Water Rate"
                ]
            )

            df = df.sort_values("Date")

            # =========================
            # PERHITUNGAN
            # =========================

            df["Total Fluid"] = (
                df["Oil Rate"] + df["Water Rate"]
            )

            df["Water Cut (%)"] = (
                df["Water Rate"]
                / df["Total Fluid"]
                * 100
            )

            # Hindari pembagian dengan nol
            df["WOR"] = df.apply(
                lambda row:
                row["Water Rate"] / row["Oil Rate"]
                if row["Oil Rate"] != 0
                else None,
                axis=1
            )

            # =========================
            # SUMMARY
            # =========================

            avg_oil = df["Oil Rate"].mean()
            avg_water = df["Water Rate"].mean()
            avg_water_cut = df["Water Cut (%)"].mean()
            avg_wor = df["WOR"].mean()

            st.write("### 📊 Production Summary")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Average Oil Rate",
                f"{avg_oil:.2f}"
            )

            col2.metric(
                "Average Water Rate",
                f"{avg_water:.2f}"
            )

            col3.metric(
                "Average Water Cut",
                f"{avg_water_cut:.2f}%"
            )

            col4.metric(
                "Average WOR",
                f"{avg_wor:.2f}"
            )
            # ==================================================
            # WELL PERFORMANCE SCORE
            # ==================================================

            st.write("### 🎯 Well Performance Score")

            # Ambil data awal dan akhir
            first_data = df.iloc[0]
            last_data = df.iloc[-1]

            first_oil = first_data["Oil Rate"]
            last_oil = last_data["Oil Rate"]

            first_wc = first_data["Water Cut (%)"]
            last_wc = last_data["Water Cut (%)"]

            first_wor = first_data["WOR"]
            last_wor = last_data["WOR"]

            # Persentase perubahan Oil Rate
            if first_oil != 0:
                oil_change_score = (
                    (last_oil - first_oil)
                    / first_oil * 100
                )
            else:
                oil_change_score = 0

            # Perubahan Water Cut
            wc_change_score = last_wc - first_wc

            # Persentase perubahan WOR
            if first_wor != 0:
                wor_change_score = (
                    (last_wor - first_wor)
                    / first_wor * 100
                )
            else:
                wor_change_score = 0

            # =========================
            # SISTEM PENILAIAN
            # =========================

            score = 100

            # Oil Rate
            if oil_change_score < -20:
                score -= 30
            elif oil_change_score < -10:
                score -= 20
            elif oil_change_score < 0:
                score -= 10

            # Water Cut
            if wc_change_score > 10:
                score -= 25
            elif wc_change_score > 5:
                score -= 15
            elif wc_change_score > 0:
                score -= 5

            # WOR
            if wor_change_score > 50:
                score -= 25
            elif wor_change_score > 20:
                score -= 15
            elif wor_change_score > 0:
                score -= 5

            # Water Cut absolut
            if last_wc >= 90:
                score -= 15
            elif last_wc >= 80:
                score -= 10

            # Pastikan score 0-100
            score = max(0, min(100, score))

            # =========================
            # KATEGORI
            # =========================

            if score >= 80:

                score_status = "🟢 GOOD"
                score_description = (
                    "Performa sumur relatif baik berdasarkan "
                    "parameter produksi yang dianalisis."
                )

            elif score >= 60:

                score_status = "🟡 MONITOR"
                score_description = (
                    "Performa sumur masih cukup baik, tetapi "
                    "terdapat parameter yang perlu dimonitor."
                )

            elif score >= 40:

                score_status = "🟠 ATTENTION"
                score_description = (
                    "Terdapat indikasi perubahan performa yang "
                    "memerlukan evaluasi lebih lanjut."
                )

            else:

                score_status = "🔴 CRITICAL"
                score_description = (
                    "Terdapat perubahan signifikan pada parameter "
                    "produksi dan diperlukan evaluasi lebih lanjut."
                )

            # =========================
            # TAMPILKAN SCORE
            # =========================

            score_col1, score_col2 = st.columns([1, 2])

            with score_col1:

                st.metric(
                    "Performance Score",
                    f"{score}/100"
                )

                st.progress(score / 100)

            with score_col2:

                st.write(f"### {score_status}")

                st.write(score_description)

            # Detail perubahan
            st.write("#### 📊 Parameter Perubahan")

            change_col1, change_col2, change_col3 = st.columns(3)

            change_col1.metric(
                "Oil Rate Change",
                f"{oil_change_score:+.1f}%"
            )

            change_col2.metric(
                "Water Cut Change",
                f"{wc_change_score:+.2f} pp"
            )

            change_col3.metric(
                "WOR Change",
                f"{wor_change_score:+.1f}%"
            )
            # =========================
            # HASIL DATA
            # =========================

            st.write("### 📋 Calculated Results")

            st.dataframe(
                df,
                use_container_width=True
            )

            # =========================
            # GRAFIK OIL RATE
            # =========================

            st.write("### 🛢️ Oil Production Trend")

            fig_oil = px.line(
                df,
                x="Date",
                y="Oil Rate",
                markers=True,
                title="Oil Rate vs Time"
            )

            st.plotly_chart(
                fig_oil,
                use_container_width=True
            )

            # =========================
            # GRAFIK WATER RATE
            # =========================

            st.write("### 💧 Water Production Trend")

            fig_water = px.line(
                df,
                x="Date",
                y="Water Rate",
                markers=True,
                title="Water Rate vs Time"
            )

            st.plotly_chart(
                fig_water,
                use_container_width=True
            )

            # =========================
            # GRAFIK WATER CUT
            # =========================

            st.write("### 💧 Water Cut Trend")

            fig_wc = px.line(
                df,
                x="Date",
                y="Water Cut (%)",
                markers=True,
                title="Water Cut vs Time"
            )

            st.plotly_chart(
                fig_wc,
                use_container_width=True
            )

            # =========================
            # GRAFIK WOR
            # =========================

            st.write("### 📊 WOR Trend")

            fig_wor = px.line(
                df,
                x="Date",
                y="WOR",
                markers=True,
                title="WOR vs Time"
            )

            st.plotly_chart(
                fig_wor,
                use_container_width=True
            )
            # ==================================================
            # TREND ANALYSIS
            # ==================================================

            st.divider()

            st.write("### 📈 Production Trend Analysis")

            # Fungsi menghitung kecenderungan tren
            def calculate_trend(series):

                values = series.dropna().reset_index(drop=True)

                n = len(values)

                if n < 2:
                    return 0, "Data tidak cukup"

                x = pd.Series(range(n))

                # Rumus slope regresi linear
                slope = (
                    ((x - x.mean()) * (values - values.mean())).sum()
                    /
                    ((x - x.mean()) ** 2).sum()
                )

                # Normalisasi terhadap nilai rata-rata
                mean_value = values.mean()

                if mean_value != 0:
                    normalized_slope = (
                        slope / mean_value * 100
                    )
                else:
                    normalized_slope = 0

                # Klasifikasi tren
                if normalized_slope > 0.10:
                    trend = "Meningkat"
                elif normalized_slope < -0.10:
                    trend = "Menurun"
                else:
                    trend = "Relatif Stabil"

                return normalized_slope, trend

            # Hitung tren setiap parameter
            oil_slope, oil_trend = calculate_trend(
                df["Oil Rate"]
            )

            water_slope, water_trend = calculate_trend(
                df["Water Rate"]
            )

            wc_slope, wc_trend = calculate_trend(
                df["Water Cut (%)"]
            )

            wor_slope, wor_trend = calculate_trend(
                df["WOR"]
            )

            # =========================
            # TABEL TREND
            # =========================

            trend_data = pd.DataFrame({
                "Parameter": [
                    "Oil Rate",
                    "Water Rate",
                    "Water Cut",
                    "WOR"
                ],

                "Trend": [
                    oil_trend,
                    water_trend,
                    wc_trend,
                    wor_trend
                ],

                "Trend Strength (% per data point)": [
                    oil_slope,
                    water_slope,
                    wc_slope,
                    wor_slope
                ]
            })

            trend_data[
                "Trend Strength (% per data point)"
            ] = trend_data[
                "Trend Strength (% per data point)"
            ].round(3)

            st.dataframe(
                trend_data,
                use_container_width=True,
                hide_index=True
            )

            # =========================
            # RINGKASAN TREND
            # =========================

            st.write("#### 🔎 Trend Summary")

            if oil_trend == "Menurun":

                st.warning(
                    "🛢️ **Oil Rate menunjukkan tren menurun.** "
                    "Hal ini menunjukkan adanya penurunan "
                    "laju produksi minyak selama periode pengamatan."
                )

            elif oil_trend == "Meningkat":

                st.success(
                    "🛢️ **Oil Rate menunjukkan tren meningkat.** "
                    "Produksi minyak menunjukkan kecenderungan positif."
                )

            else:

                st.info(
                    "🛢️ **Oil Rate relatif stabil.**"
                )

            if water_trend == "Meningkat":

                st.warning(
                    "💧 **Water Rate menunjukkan tren meningkat.** "
                    "Produksi air cenderung bertambah selama "
                    "periode pengamatan."
                )

            elif water_trend == "Menurun":

                st.success(
                    "💧 **Water Rate menunjukkan tren menurun.**"
                )

            else:

                st.info(
                    "💧 **Water Rate relatif stabil.**"
                )

            if wc_trend == "Meningkat":

                st.warning(
                    "💧 **Water Cut menunjukkan tren meningkat.** "
                    "Proporsi air dalam total produksi cenderung "
                    "semakin besar."
                )

            elif wc_trend == "Menurun":

                st.success(
                    "💧 **Water Cut menunjukkan tren menurun.**"
                )

            else:

                st.info(
                    "💧 **Water Cut relatif stabil.**"
                )

            if wor_trend == "Meningkat":

                st.warning(
                    "📊 **WOR menunjukkan tren meningkat.** "
                    "Rasio produksi air terhadap minyak cenderung "
                    "semakin besar."
                )

            elif wor_trend == "Menurun":

                st.success(
                    "📊 **WOR menunjukkan tren menurun.**"
                )

            else:

                st.info(
                    "📊 **WOR relatif stabil.**"
                )

            # =========================
            # COMBINED TREND ASSESSMENT
            # =========================

            st.write("#### 🚨 Combined Trend Assessment")

            if (
                oil_trend == "Menurun"
                and (
                    water_trend == "Meningkat"
                    or wc_trend == "Meningkat"
                    or wor_trend == "Meningkat"
                )
            ):

                st.error(
                    "🔴 **Perlu perhatian:** Oil Rate menunjukkan "
                    "tren menurun sementara parameter produksi air "
                    "menunjukkan tren meningkat. Kombinasi ini "
                    "mengindikasikan penurunan performa produksi "
                    "yang perlu dievaluasi lebih lanjut."
                )

            elif (
                oil_trend == "Menurun"
                and water_trend == "Menurun"
                and wc_trend == "Relatif Stabil"
            ):

                st.warning(
                    "🟡 **Monitoring diperlukan:** Oil Rate menurun "
                    "bersamaan dengan penurunan Water Rate. "
                    "Perlu evaluasi lebih lanjut untuk memahami "
                    "penyebab penurunan produksi."
                )

            elif (
                oil_trend == "Meningkat"
                and wc_trend != "Meningkat"
                and wor_trend != "Meningkat"
            ):

                st.success(
                    "🟢 **Kondisi relatif positif:** Oil Rate "
                    "menunjukkan tren meningkat tanpa peningkatan "
                    "signifikan pada kontribusi air."
                )

            else:

                st.info(
                    "🟡 **Kondisi perlu dimonitor:** Belum terdapat "
                    "kombinasi tren yang menunjukkan kondisi ekstrem. "
                    "Monitoring parameter produksi tetap diperlukan."
                )
                # ==================================================
            # RISK FLAG
            # ==================================================

            st.divider()

            st.write("### 🚨 Production Risk Assessment")

            # Menggunakan hasil Trend Analysis
            risk_score = 0
            risk_reasons = []

            # ----------------------------------
            # 1. OIL RATE
            # ----------------------------------

            if oil_trend == "Menurun":
                risk_score += 2
                risk_reasons.append(
                    "Oil Rate menunjukkan tren menurun."
                )

            # ----------------------------------
            # 2. WATER RATE
            # ----------------------------------

            if water_trend == "Meningkat":
                risk_score += 2
                risk_reasons.append(
                    "Water Rate menunjukkan tren meningkat."
                )

            # ----------------------------------
            # 3. WATER CUT
            # ----------------------------------

            if wc_trend == "Meningkat":
                risk_score += 2
                risk_reasons.append(
                    "Water Cut menunjukkan tren meningkat."
                )

            # ----------------------------------
            # 4. WOR
            # ----------------------------------

            if wor_trend == "Meningkat":
                risk_score += 2
                risk_reasons.append(
                    "WOR menunjukkan tren meningkat."
                )

            # ----------------------------------
            # 5. WATER CUT ABSOLUT
            # ----------------------------------

            if last_wc >= 90:

                risk_score += 3

                risk_reasons.append(
                    f"Water Cut akhir mencapai {last_wc:.1f}%."
                )

            elif last_wc >= 80:

                risk_score += 2

                risk_reasons.append(
                    f"Water Cut akhir mencapai {last_wc:.1f}%."
                )

            elif last_wc >= 70:

                risk_score += 1

                risk_reasons.append(
                    f"Water Cut akhir mencapai {last_wc:.1f}%."
                )

            # ==================================================
            # KATEGORI RISIKO
            # ==================================================

            if risk_score <= 2:

                risk_level = "🟢 LOW RISK"

                risk_message = (
                    "Tidak terdapat indikasi perubahan performa "
                    "yang signifikan berdasarkan parameter yang dianalisis."
                )

            elif risk_score <= 5:

                risk_level = "🟡 MEDIUM RISK"

                risk_message = (
                    "Terdapat beberapa perubahan parameter produksi "
                    "yang perlu dimonitor."
                )

            elif risk_score <= 8:

                risk_level = "🟠 HIGH RISK"

                risk_message = (
                    "Terdapat indikasi penurunan performa atau "
                    "peningkatan kontribusi air yang cukup signifikan."
                )

            else:

                risk_level = "🔴 CRITICAL RISK"

                risk_message = (
                    "Terdapat kombinasi perubahan parameter produksi "
                    "yang signifikan dan memerlukan evaluasi engineering "
                    "lebih lanjut."
                )

            # ==================================================
            # TAMPILKAN RISK
            # ==================================================

            risk_col1, risk_col2 = st.columns([1, 2])

            with risk_col1:

                st.metric(
                    "Risk Score",
                    f"{risk_score}/11"
                )

            with risk_col2:

                st.write(f"## {risk_level}")
                st.write(risk_message)

            # ==================================================
            # RISK FACTORS
            # ==================================================

            if risk_reasons:

                st.write("#### ⚠️ Risk Factors")

                for reason in risk_reasons:

                    st.write(
                        f"• {reason}"
                    )

            else:

                st.write(
                    "#### ✅ Tidak ditemukan risk factor utama."
                )

            # ==================================================
            # ENGINEERING RECOMMENDATION
            # ==================================================

            st.write("### 🛠️ Engineering Recommendation")

            if (
                oil_trend == "Menurun"
                and wc_trend == "Meningkat"
                and wor_trend == "Meningkat"
            ):
                recommendation_title = (
                    "⚠️ Indikasi Penurunan Performa dan Peningkatan Kontribusi Air"
                )
                recommendation_text = (
                    "Oil Rate menunjukkan tren menurun sementara Water Cut dan WOR "
                    "meningkat. Kombinasi ini menunjukkan bahwa kontribusi air "
                    "terhadap produksi semakin besar dibandingkan minyak."
                )
                engineering_action = [
                    "Evaluasi tren Oil Rate, Water Cut, dan WOR pada well test berikutnya.",
                    "Periksa perubahan performa artificial lift apabila sumur menggunakan ESP.",
                    "Evaluasi kemungkinan peningkatan water production atau perubahan kondisi aliran.",
                    "Bandingkan kondisi produksi dengan periode well test sebelumnya.",
                    "Jika data reservoir tersedia, lakukan evaluasi lebih lanjut terhadap sumber peningkatan produksi air."
                ]

            elif oil_trend == "Menurun" and water_trend == "Meningkat":
                recommendation_title = (
                    "⚠️ Penurunan Oil Rate dengan Peningkatan Water Rate"
                )
                recommendation_text = (
                    "Produksi minyak menunjukkan kecenderungan menurun sementara "
                    "produksi air meningkat. Kondisi ini perlu dimonitor karena "
                    "dapat menyebabkan penurunan kontribusi minyak terhadap total produksi."
                )
                engineering_action = [
                    "Monitor perubahan Water Cut dan WOR.",
                    "Evaluasi hasil well test secara berkala.",
                    "Periksa performa artificial lift jika tersedia.",
                    "Bandingkan laju produksi minyak dan air antar-periode.",
                    "Investigasi lebih lanjut diperlukan apabila tren berlangsung secara konsisten."
                ]

            elif wc_trend == "Meningkat" or wor_trend == "Meningkat":
                recommendation_title = "💧 Peningkatan Kontribusi Air"
                recommendation_text = (
                    "Water Cut atau WOR menunjukkan tren meningkat. Hal ini "
                    "mengindikasikan bahwa proporsi produksi air terhadap minyak "
                    "cenderung meningkat selama periode pengamatan."
                )
                engineering_action = [
                    "Monitor Water Cut dan WOR pada well test berikutnya.",
                    "Evaluasi perkembangan Water Rate.",
                    "Identifikasi apakah peningkatan berlangsung secara bertahap atau mendadak.",
                    "Evaluasi kondisi artificial lift apabila perubahan produksi cukup signifikan.",
                    "Jika data reservoir tersedia, lakukan evaluasi mekanisme masuknya air."
                ]

            elif (
                oil_trend == "Meningkat"
                and wc_trend != "Meningkat"
                and wor_trend != "Meningkat"
            ):
                recommendation_title = "✅ Performa Produksi Relatif Positif"
                recommendation_text = (
                    "Oil Rate menunjukkan tren meningkat tanpa diikuti peningkatan "
                    "signifikan pada Water Cut maupun WOR. Kondisi ini menunjukkan "
                    "kecenderungan performa produksi yang positif."
                )
                engineering_action = [
                    "Pertahankan monitoring produksi secara berkala.",
                    "Monitor Water Cut dan WOR untuk memastikan kontribusi air tetap terkendali.",
                    "Evaluasi kestabilan performa artificial lift apabila digunakan.",
                    "Dokumentasikan perubahan produksi sebagai dasar evaluasi periode berikutnya."
                ]

            else:
                recommendation_title = "ℹ️ Performa Produksi Memerlukan Monitoring"
                recommendation_text = (
                    "Belum terdapat kombinasi perubahan parameter yang menunjukkan "
                    "kondisi ekstrem. Namun, perubahan Oil Rate, Water Rate, "
                    "Water Cut, dan WOR tetap perlu dipantau secara berkala."
                )
                engineering_action = [
                    "Lakukan monitoring rutin terhadap parameter produksi.",
                    "Bandingkan hasil well test antar-periode.",
                    "Perhatikan perubahan Water Cut dan WOR.",
                    "Evaluasi lebih lanjut apabila terjadi perubahan tren yang signifikan."
                ]

            if "⚠️" in recommendation_title or "💧" in recommendation_title:
                st.warning(recommendation_title)
            elif "✅" in recommendation_title:
                st.success(recommendation_title)
            else:
                st.info(recommendation_title)

            st.write(f"**Interpretasi:** {recommendation_text}")
            st.write("##### 📋 Recommended Engineering Actions")

            for action in engineering_action:
                st.write(f"• {action}")

            st.caption(
                "Rekomendasi merupakan screening berbasis data produksi dan "
                "rule-based petroleum engineering. Hasil ini tidak menggantikan "
                "analisis engineering secara menyeluruh."
            )

           # ==================================================
            # PETROLEUM PRODUCTION EXPERT SYSTEM
            # ==================================================

            st.divider()

            st.write("### 🧠 Petroleum Production Expert Analysis")

            # Ambil data awal dan akhir
            first = df.iloc[0]
            last = df.iloc[-1]

            first_oil = first["Oil Rate"]
            last_oil = last["Oil Rate"]

            first_water = first["Water Rate"]
            last_water = last["Water Rate"]

            first_wc = first["Water Cut (%)"]
            last_wc = last["Water Cut (%)"]

            first_wor = first["WOR"]
            last_wor = last["WOR"]

            # =========================
            # HITUNG PERUBAHAN
            # =========================

            oil_change = (
                (last_oil - first_oil)
                / first_oil * 100
                if first_oil != 0 else 0
            )

            water_change = (
                (last_water - first_water)
                / first_water * 100
                if first_water != 0 else 0
            )

            wc_change = last_wc - first_wc

            wor_change = (
                (last_wor - first_wor)
                / first_wor * 100
                if first_wor != 0 else 0
            )

            # =========================
            # INTERPRETASI OIL
            # =========================

            if oil_change > 10:

                oil_analysis = (
                    f"Oil Rate meningkat sebesar {oil_change:.1f}% "
                    "selama periode pengamatan."
                )

            elif oil_change < -10:

                oil_analysis = (
                    f"Oil Rate menurun sebesar "
                    f"{abs(oil_change):.1f}% selama periode pengamatan."
                )

            else:

                oil_analysis = (
                    "Oil Rate relatif stabil selama "
                    "periode pengamatan."
                )

            # =========================
            # INTERPRETASI WATER
            # =========================

            if water_change > 10:

                water_analysis = (
                    f"Water Rate meningkat sebesar "
                    f"{water_change:.1f}%."
                )

            elif water_change < -10:

                water_analysis = (
                    f"Water Rate menurun sebesar "
                    f"{abs(water_change):.1f}%."
                )

            else:

                water_analysis = (
                    "Water Rate relatif stabil."
                )

            # =========================
            # INTERPRETASI WATER CUT
            # =========================

            if wc_change > 5:

                wc_analysis = (
                    f"Water Cut meningkat sebesar "
                    f"{wc_change:.2f} percentage points. "
                    "Kontribusi air terhadap total produksi "
                    "menunjukkan kecenderungan meningkat."
                )

            elif wc_change < -5:

                wc_analysis = (
                    f"Water Cut menurun sebesar "
                    f"{abs(wc_change):.2f} percentage points. "
                    "Proporsi air terhadap total produksi "
                    "menunjukkan kecenderungan menurun."
                )

            else:

                wc_analysis = (
                    "Water Cut relatif stabil selama "
                    "periode pengamatan."
                )

            # =========================
            # INTERPRETASI WOR
            # =========================

            if wor_change > 20:

                wor_analysis = (
                    f"WOR meningkat sebesar {wor_change:.1f}%. "
                    "Hal ini menunjukkan bahwa rasio produksi air "
                    "terhadap minyak semakin besar."
                )

            elif wor_change < -20:

                wor_analysis = (
                    f"WOR menurun sebesar {abs(wor_change):.1f}%. "
                    "Rasio produksi air terhadap minyak "
                    "menunjukkan kecenderungan menurun."
                )

            else:

                wor_analysis = (
                    "WOR relatif stabil selama "
                    "periode pengamatan."
                )

            # =========================
            # KONDISI PRODUKSI
            # =========================

            if (
                oil_change < -10
                and wc_change > 5
                and wor_change > 20
            ):

                condition = (
                    "⚠️ **Perlu perhatian:** "
                    "Oil Rate menurun sementara Water Cut dan WOR "
                    "meningkat. Kondisi ini menunjukkan peningkatan "
                    "dominasi air dalam produksi sumur."
                )

                recommendation = (
                    "Disarankan melakukan evaluasi lebih lanjut "
                    "terhadap performa sumur, kontribusi air, "
                    "serta kondisi artificial lift apabila digunakan."
                )

            elif (
                wc_change > 5
                or wor_change > 20
            ):

                condition = (
                    "⚠️ **Peningkatan kontribusi air terindikasi:** "
                    "Water Cut atau WOR menunjukkan kecenderungan meningkat."
                )

                recommendation = (
                    "Disarankan memonitor perkembangan Water Cut "
                    "dan WOR pada periode berikutnya serta mengevaluasi "
                    "performa produksi sumur."
                )

            elif oil_change > 10:

                condition = (
                    "✅ **Performa produksi positif:** "
                    "Oil Rate menunjukkan peningkatan."
                )

                recommendation = (
                    "Pertahankan monitoring produksi dan evaluasi "
                    "tren Water Cut serta WOR secara berkala."
                )

            else:

                condition = (
                    "ℹ️ **Performa relatif stabil:** "
                    "Tidak terlihat perubahan ekstrem pada parameter utama."
                )

                recommendation = (
                    "Lanjutkan monitoring berkala terhadap Oil Rate, "
                    "Water Rate, Water Cut, dan WOR."
                )

            # =========================
            # TAMPILKAN ANALISIS
            # =========================

            st.info(condition)

            st.write("#### 🔎 Hasil Analisis")

            st.write(
                f"**1. Oil Rate:** {oil_analysis}"
            )

            st.write(
                f"**2. Water Rate:** {water_analysis}"
            )

            st.write(
                f"**3. Water Cut:** {wc_analysis}"
            )

            st.write(
                f"**4. WOR:** {wor_analysis}"
            )

            st.write("#### 💡 Rekomendasi")

            st.success(recommendation)

            st.caption(
                "Catatan: hasil analisis merupakan indikasi awal "
                "berdasarkan data produksi dan tidak menggantikan "
                "analisis engineering yang lebih lengkap."
            )


            # ==================================================
            # AUTO PDF REPORT
            # ==================================================

            st.divider()

            st.write("### 📄 Automatic Engineering Report")

            st.write(
                "Generate laporan PDF yang berisi ringkasan produksi, "
                "performance score, trend analysis, risk flag, "
                "engineering recommendation, dan grafik."
            )

            if st.button("📄 Generate PDF Report", type="primary"):

                try:

                    # ------------------------------
                    # BUAT PDF DI MEMORY
                    # ------------------------------

                    pdf_buffer = BytesIO()

                    styles = getSampleStyleSheet()

                    title_style = ParagraphStyle(
                        "CustomTitle",
                        parent=styles["Title"],
                        alignment=TA_CENTER,
                        fontSize=20,
                        spaceAfter=12
                    )

                    heading_style = ParagraphStyle(
                        "CustomHeading",
                        parent=styles["Heading2"],
                        fontSize=14,
                        spaceBefore=10,
                        spaceAfter=8
                    )

                    normal_style = ParagraphStyle(
                        "CustomNormal",
                        parent=styles["BodyText"],
                        fontSize=9,
                        leading=13
                    )

                    doc = SimpleDocTemplate(
                        pdf_buffer,
                        pagesize=A4,
                        rightMargin=1.5 * cm,
                        leftMargin=1.5 * cm,
                        topMargin=1.5 * cm,
                        bottomMargin=1.5 * cm
                    )

                    story = []

                    # ------------------------------
                    # JUDUL
                    # ------------------------------

                    story.append(
                        Paragraph(
                            "PETROAI ANALYZER",
                            title_style
                        )
                    )

                    story.append(
                        Paragraph(
                            "Petroleum Production Engineering Report",
                            styles["Heading2"]
                        )
                    )

                    story.append(
                        Spacer(1, 0.3 * cm)
                    )

                    story.append(
                        Paragraph(
                            f"<b>Data Period:</b> "
                            f"{df['Date'].min().strftime('%d %b %Y')} - "
                            f"{df['Date'].max().strftime('%d %b %Y')}",
                            normal_style
                        )
                    )

                    story.append(
                        Paragraph(
                            f"<b>Total Data Points:</b> {len(df)}",
                            normal_style
                        )
                    )

                    story.append(Spacer(1, 0.4 * cm))

                    # ------------------------------
                    # PRODUCTION SUMMARY
                    # ------------------------------

                    story.append(
                        Paragraph(
                            "1. Production Summary",
                            heading_style
                        )
                    )

                    summary_data = [
                        ["Parameter", "Average"],
                        ["Oil Rate", f"{avg_oil:.2f}"],
                        ["Water Rate", f"{avg_water:.2f}"],
                        ["Water Cut", f"{avg_water_cut:.2f}%"],
                        ["WOR", f"{avg_wor:.2f}"]
                    ]

                    summary_table = Table(
                        summary_data,
                        colWidths=[8 * cm, 6 * cm]
                    )

                    summary_table.setStyle(
                        TableStyle([
                            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                            ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ])
                    )

                    story.append(summary_table)
                    story.append(Spacer(1, 0.4 * cm))

                    # ------------------------------
                    # PERFORMANCE SCORE
                    # ------------------------------

                    story.append(
                        Paragraph(
                            "2. Well Performance Score",
                            heading_style
                        )
                    )

                    score_data = [
                        ["Indicator", "Result"],
                        ["Performance Score", f"{score}/100"],
                        ["Status", score_status],
                        ["Oil Rate Change", f"{oil_change_score:+.1f}%"],
                        ["Water Cut Change", f"{wc_change_score:+.2f} pp"],
                        ["WOR Change", f"{wor_change_score:+.1f}%"]
                    ]

                    score_table = Table(
                        score_data,
                        colWidths=[8 * cm, 6 * cm]
                    )

                    score_table.setStyle(
                        TableStyle([
                            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                            ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ])
                    )

                    story.append(score_table)
                    story.append(
                        Paragraph(
                            score_description,
                            normal_style
                        )
                    )

                    # ------------------------------
                    # TREND ANALYSIS
                    # ------------------------------

                    story.append(
                        Paragraph(
                            "3. Trend Analysis",
                            heading_style
                        )
                    )

                    trend_data = [
                        ["Parameter", "Trend", "Strength"],
                        [
                            "Oil Rate",
                            oil_trend,
                            f"{oil_slope:.3f}%"
                        ],
                        [
                            "Water Rate",
                            water_trend,
                            f"{water_slope:.3f}%"
                        ],
                        [
                            "Water Cut",
                            wc_trend,
                            f"{wc_slope:.3f}%"
                        ],
                        [
                            "WOR",
                            wor_trend,
                            f"{wor_slope:.3f}%"
                        ]
                    ]

                    trend_table = Table(
                        trend_data,
                        colWidths=[5 * cm, 5 * cm, 4 * cm]
                    )

                    trend_table.setStyle(
                        TableStyle([
                            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                            ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ])
                    )

                    story.append(trend_table)

                    # ------------------------------
                    # RISK FLAG
                    # ------------------------------

                    story.append(
                        Paragraph(
                            "4. Production Risk Assessment",
                            heading_style
                        )
                    )

                    story.append(
                        Paragraph(
                            f"<b>Risk Score:</b> {risk_score}/11",
                            normal_style
                        )
                    )

                    story.append(
                        Paragraph(
                            f"<b>Risk Level:</b> {risk_level}",
                            normal_style
                        )
                    )

                    story.append(
                        Paragraph(
                            risk_message,
                            normal_style
                        )
                    )

                    if risk_reasons:

                        story.append(
                            Paragraph(
                                "<b>Risk Factors:</b>",
                                normal_style
                            )
                        )

                        for reason in risk_reasons:

                            story.append(
                                Paragraph(
                                    f"• {reason}",
                                    normal_style
                                )
                            )

                    # ------------------------------
                    # ENGINEERING RECOMMENDATION
                    # ------------------------------

                    story.append(
                        Paragraph(
                            "5. Engineering Recommendation",
                            heading_style
                        )
                    )

                    story.append(
                        Paragraph(
                            f"<b>{recommendation_title}</b>",
                            normal_style
                        )
                    )

                    story.append(
                        Paragraph(
                            recommendation_text,
                            normal_style
                        )
                    )

                    story.append(
                        Paragraph(
                            "<b>Recommended Engineering Actions:</b>",
                            normal_style
                        )
                    )

                    for action in engineering_action:

                        story.append(
                            Paragraph(
                                f"• {action}",
                                normal_style
                            )
                        )

                    # ------------------------------
                    # EXPERT ANALYSIS
                    # ------------------------------

                    story.append(
                        Paragraph(
                            "6. Petroleum Production Expert Analysis",
                            heading_style
                        )
                    )

                    story.append(
                        Paragraph(
                            f"<b>Oil Rate:</b> {oil_analysis}",
                            normal_style
                        )
                    )

                    story.append(
                        Paragraph(
                            f"<b>Water Rate:</b> {water_analysis}",
                            normal_style
                        )
                    )

                    story.append(
                        Paragraph(
                            f"<b>Water Cut:</b> {wc_analysis}",
                            normal_style
                        )
                    )

                    story.append(
                        Paragraph(
                            f"<b>WOR:</b> {wor_analysis}",
                            normal_style
                        )
                    )

                    story.append(
                        Paragraph(
                            f"<b>Overall Condition:</b> {condition}",
                            normal_style
                        )

                    )

                    story.append(
                        Paragraph(
                            f"<b>Recommendation:</b> {recommendation}",
                            normal_style
                        )
                    )

                    # ------------------------------
                    # GRAPHICS
                    # ------------------------------

                    story.append(PageBreak())

                    story.append(
                        Paragraph(
                            "7. Production Charts",
                            heading_style
                        )
                    )

                    chart_specs = [
                        ("Oil Rate", "Oil Rate vs Time", "Oil Rate"),
                        ("Water Rate", "Water Rate vs Time", "Water Rate"),
                        ("Water Cut (%)", "Water Cut vs Time", "Water Cut (%)"),
                        ("WOR", "WOR vs Time", "WOR")
                    ]

                    for column, title, ylabel in chart_specs:

                        fig = plt.figure(figsize=(7.2, 3.5))
                        ax = fig.add_subplot(111)

                        ax.plot(
                            df["Date"],
                            df[column],
                            marker="o",
                            linewidth=1
                        )

                        ax.set_title(title)
                        ax.set_xlabel("Date")
                        ax.set_ylabel(ylabel)
                        ax.grid(True, alpha=0.3)

                        fig.autofmt_xdate()

                        image_buffer = BytesIO()

                        fig.savefig(
                            image_buffer,
                            format="png",
                            dpi=150,
                            bbox_inches="tight"
                        )

                        plt.close(fig)

                        image_buffer.seek(0)

                        story.append(
                            Image(
                                image_buffer,
                                width=17 * cm,
                                height=8.2 * cm
                            )
                        )

                        story.append(
                            Spacer(1, 0.2 * cm)
                        )

                    # ------------------------------
                    # CATATAN
                    # ------------------------------

                    story.append(PageBreak())

                    story.append(
                        Paragraph(
                            "8. Engineering Note",
                            heading_style
                        )
                    )

                    story.append(
                        Paragraph(
                            "Laporan ini merupakan hasil screening berbasis "
                            "data produksi menggunakan rule-based petroleum "
                            "engineering analysis. Hasil tidak dimaksudkan "
                            "sebagai diagnosis pasti terhadap kondisi "
                            "reservoir atau sumur dan perlu dikonfirmasi "
                            "dengan data engineering tambahan apabila tersedia.",
                            normal_style
                        )
                    )

                    doc.build(story)

                    pdf_buffer.seek(0)

                    st.success(
                        "✅ PDF report berhasil dibuat!"
                    )

                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=pdf_buffer,
                        file_name="PetroAI_Engineering_Report.pdf",
                        mime="application/pdf"
                    )

                except Exception as pdf_error:

                    st.error(
                        f"❌ Gagal membuat PDF: {pdf_error}"
                    )


    except Exception as e:

        st.error(
            f"❌ Terjadi kesalahan saat membaca data: {e}"
        )

else:

    st.info(
        "👆 Silakan upload file Excel atau CSV "
        "untuk memulai analisis."
    )