if recommendations:
    st.subheader(f"Top 10 similar movies to '{selected_movie}':")
    for idx, (title, score) in enumerate(recommendations):
        st.markdown(f"### 🎬 {title} ({score*100:.1f}%)")
        poster, overview, reviews = fetch_movie_details(title)
        if poster:
            st.image(poster, width=220)
        st.write(f"📖 {overview}")
        trailer_url = fetch_trailer_url(title)
        if trailer_url:
            st.video(trailer_url)
        st.markdown("📝 **Reviews:**")
        for review in reviews:
            st.markdown(f"- {review}")

        # ✅ Add this line for unique text area
        st.text_area(
            "Write your own review:",
            key=f"user_review_{idx}_{title}"
        )

<<<<<<< HEAD
# ✅ Streamlit UI
def main():
    st.set_page_config(page_title="🎬 Movie Recommender + AI", layout="centered")
    st.title("🎬 Movie Recommendation Engine with Posters, Reviews, Trailers & AI")

    df_full = load_data()
    language_list = ['all'] + sorted(df_full['language'].dropna().unique())
    selected_language = st.selectbox("🌐 Filter by Language", language_list, key="language_filter")

    df = df_full if selected_language == 'all' else df_full[df_full['language'] == selected_language]
    if df.empty:
        st.warning("No movies found for this language.")
        return

    similarity = compute_similarity(df)
    movie_list = df['title'].values
    selected_movie = st.selectbox("🎥 Choose a movie to get recommendations:", movie_list, key="movie_select")

    # Only define and use recommendations after the button is pressed
    if st.button("🎯 Recommend"):
        recommendations = recommend(selected_movie, df, similarity)
        if recommendations:
            st.subheader(f"Top 10 similar movies to '{selected_movie}':")
            for title, score in recommendations:
                st.markdown(f"### 🎬 {title} ({score*100:.1f}%)")
                poster, overview, reviews = fetch_movie_details(title)
                if poster:
                    st.image(poster, width=220)
                st.write(f"📖 {overview}")
                trailer_url = fetch_trailer_url(title)
                if trailer_url:
                    st.video(trailer_url)
                st.markdown("📝 **Reviews:**")
                for review in reviews:
                    st.markdown(f"- {review}")
                st.markdown("---")
        else:
            st.warning("Movie not found in dataset.")

    st.sidebar.header("💬 Ask AI Assistant")
    user_input = st.sidebar.text_area("Ask about movies, moods, platforms...", key="ai_input")
    if st.sidebar.button("Ask AI"):
        with st.spinner("Thinking..."):
            answer = chat_with_ai(user_input)
            st.sidebar.success("Answer:")
            st.sidebar.write(answer)

if __name__ == "__main__":
    main()
=======
        st.markdown("---")
>>>>>>> b67cc04eb387f23c3936566a356dea2c6d8c8101
