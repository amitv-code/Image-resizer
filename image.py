import streamlit as st
from PIL import Image
import io
import os
from zipfile import ZipFile

def process_image(image, width, height, quality):
    img = Image.open(image)
    resized = img.resize((width, height), Image.Resampling.LANCZOS)
    img_bytes = io.BytesIO()
    resized.save(img_bytes, format='WEBP', quality=quality)
    img_bytes.seek(0)
    return img_bytes

def main():
    st.title("📸 Bulk Image Resizer & WebP Converter")
    
    with st.sidebar:
        st.header("Settings")
        width = st.number_input("Width (pixels)", min_value=1, value=800)
        height = st.number_input("Height (pixels)", min_value=1, value=600)
        quality = st.slider("WebP Quality", 1, 100, 80)
        bulk_mode = st.checkbox("Bulk Process Multiple Images")
    
    # ——————— Wrap uploader into a list ———————
    raw_upload = st.file_uploader(
        "Upload Images (PNG/JPG)",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=bulk_mode
    )
    if not raw_upload:
        uploaded_files = []
    elif isinstance(raw_upload, list):
        uploaded_files = raw_upload
    else:
        uploaded_files = [raw_upload]
    # ————————————————————————————————————————

    if uploaded_files and st.button("Process Images"):
        processed_files = []
        
        with st.status("Processing images...", expanded=True) as status:
            for uploaded_file in uploaded_files:
                try:
                    result = process_image(uploaded_file, width, height, quality)
                    name_root = os.path.splitext(uploaded_file.name)[0]
                    new_name = f"{name_root}_{width}x{height}.webp"
                    processed_files.append((new_name, result))
                    st.write(f"✅ {uploaded_file.name} processed")
                except Exception as e:
                    st.error(f"Failed to process {uploaded_file.name}: {e}")
        
        status.update(label="Processing complete!", state="complete", expanded=False)
        
        st.subheader("Download Options")
        if bulk_mode:
            zip_buffer = io.BytesIO()
            with ZipFile(zip_buffer, 'w') as zip_file:
                for name, data in processed_files:
                    zip_file.writestr(name, data.getvalue())
            st.download_button(
                label="📦 Download All as ZIP",
                data=zip_buffer.getvalue(),
                file_name="processed_images.zip",
                mime="application/zip"
            )
            with st.expander("📤 Download Individual Files"):
                for name, data in processed_files:
                    st.download_button(
                        label=f"⬇️ {name}",
                        data=data.getvalue(),
                        file_name=name,
                        mime="image/webp"
                    )
        else:
            name, data = processed_files[0]
            st.download_button(
                label="📥 Download Image",
                data=data.getvalue(),
                file_name=name,
                mime="image/webp"
            )

if __name__ == "__main__":
    main()