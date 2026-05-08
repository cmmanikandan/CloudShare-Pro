import cloudinary.api

class AIService:
    @staticmethod
    def analyze_image(public_id):
        """
        Uses Cloudinary AI to analyze and tag an image.
        Requires Cloudinary AI Tagging add-on.
        """
        try:
            result = cloudinary.api.resource(public_id, colors=True, image_metadata=True)
            tags = result.get('tags', [])
            return {
                'tags': tags,
                'colors': result.get('colors', []),
                'format': result.get('format')
            }
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def categorize_file(mime_type):
        """Simple AI categorization based on mime type."""
        if not mime_type:
            return 'other'
        
        mime_type = mime_type.lower()
        if 'image' in mime_type:
            return 'image'
        if 'video' in mime_type:
            return 'video'
        if 'pdf' in mime_type:
            return 'document'
        if 'zip' in mime_type or 'rar' in mime_type:
            return 'archive'
        
        return 'other'
