import cloudinary
import cloudinary.uploader
import cloudinary.api

class CloudinaryService:
    @staticmethod
    def upload_file(file, folder="cloudsharepro"):
        """Uploads a file to Cloudinary and returns the result."""
        from flask import current_app
        params = {
            "folder": folder,
            "resource_type": "auto"
        }
        
        # Use preset if available (for unsigned uploads)
        if current_app.config.get('CLOUDINARY_UPLOAD_PRESET'):
            params['upload_preset'] = current_app.config['CLOUDINARY_UPLOAD_PRESET']
            
        return cloudinary.uploader.upload(file, **params)

    @staticmethod
    def delete_file(public_id):
        """Deletes a file from Cloudinary."""
        return cloudinary.uploader.destroy(public_id)

    @staticmethod
    def get_optimized_url(public_id, format="webp"):
        """Generates an optimized URL for an image/video."""
        return cloudinary.utils.cloudinary_url(
            public_id,
            fetch_format=format,
            quality="auto"
        )[0]
