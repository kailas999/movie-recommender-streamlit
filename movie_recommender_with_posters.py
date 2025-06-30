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

        st.markdown("---")
