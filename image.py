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
    
    # Add this at the beginning of your main() function
    st.markdown("""
    <style>
        section[data-testid="stFileUploaderDropzone"] {
            min-height: 250px !important;
            border: 2px dashed #1e88e5 !important;
            border-radius: 10px !important;
            background-color: #f0f2f6 !important;
            transition: all 0.3s ease !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
        }

        section[data-testid="stFileUploaderDropzone"]:hover {
            border-color: #0d47a1 !important;
            background-color: #dddd !important;
        }

        div[data-testid="stFileUploaderDropzoneInstructions"] {
            text-align: center !important;
            padding: 20px !important;
        }

        .st-emotion-cache-wn8ljn { /* Cloud icon container */
            margin-bottom: 1rem !important;
        }

        .st-emotion-cache-9ycgxx { /* "Drag and drop files here" text */
            font-size: 1.2rem !important;
            font-weight: 500 !important;
            color: #1e88e5 !important;
        }

        .st-emotion-cache-7oyrr6 { /* "Limit 200MB..." text */
            color: #666 !important;
            margin-top: 0.5rem !important;
        }

        button[data-testid="stBaseButton-secondary"] { /* Browse files button */
            margin-top: 1rem !important;
            padding: 8px 20px !important;
            background-color: #1e88e5 !important;
            color: white !important;
            border: none !important;
        }

        button[data-testid="stBaseButton-secondary"]:hover {
            background-color: #0d47a1 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = []
    
    with st.sidebar:
        st.header("Settings")
        width = st.number_input("Width (pixels)", min_value=1, value=500)
        height = st.number_input("Height (pixels)", min_value=1, value=500)
        quality = st.slider("WebP Quality", 1, 100, 80)
        bulk_mode = st.checkbox("Bulk Process Multiple Images", value=True)
    
    # Enhanced file uploader
    uploaded_files = st.file_uploader(
        "Drag and drop images here (PNG/JPG/WebP)",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=bulk_mode,
        help="Upload images to resize and convert to WebP format"
    )

    process_clicked = st.button("Process Images")
    
    if process_clicked and uploaded_files:
        st.session_state.processed_files = []
        
        with st.status("Processing images...", expanded=True) as status:
            for uploaded_file in uploaded_files:
                try:
                    result = process_image(uploaded_file, width, height, quality)
                    name_root = os.path.splitext(uploaded_file.name)[0]
                    new_name = f"{name_root}_{width}x{height}.webp"
                    st.session_state.processed_files.append((new_name, result))
                    st.write(f"✅ {uploaded_file.name} processed")
                except Exception as e:
                    st.error(f"Failed to process {uploaded_file.name}: {e}")
        
        status.update(label="Processing complete!", state="complete", expanded=False)

    if st.session_state.processed_files:
        st.subheader("Download Options")
        if bulk_mode:
            zip_buffer = io.BytesIO()
            with ZipFile(zip_buffer, 'w') as zip_file:
                for name, data in st.session_state.processed_files:
                    zip_file.writestr(name, data.getvalue())
            st.download_button(
                label="📦 Download All as ZIP",
                data=zip_buffer.getvalue(),
                file_name="processed_images.zip",
                mime="application/zip"
            )
            with st.expander("📤 Download Individual Files"):
                for name, data in st.session_state.processed_files:
                    st.download_button(
                        label=f"⬇️ {name}",
                        data=data.getvalue(),
                        file_name=name,
                        mime="image/webp",
                        key=f"dl_{name}"
                    )
        else:
            name, data = st.session_state.processed_files[0]
            st.download_button(
                label="📥 Download Image",
                data=data.getvalue(),
                file_name=name,
                mime="image/webp"
            )

if __name__ == "__main__":
    main()