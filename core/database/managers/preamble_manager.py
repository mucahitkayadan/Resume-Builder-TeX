from typing import Optional, List, Dict, Any

class PreambleManager:
    """Handles all preamble-related database operations"""
    def __init__(self, connection):
        self.conn = connection
        
    def get_preamble(self, template_id: int = 1) -> Optional[str]:
        """Retrieve a LaTeX preamble by template ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT content FROM preambles WHERE id = ?', (template_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """List all available templates"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, name, description FROM preambles')
        return [
            {'id': row[0], 'name': row[1], 'description': row[2]}
            for row in cursor.fetchall()
        ]
    
    def add_template(self, name: str, content: str, description: str = '') -> int:
        """Add a new template"""
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO preambles (name, content, description) VALUES (?, ?, ?)',
            (name, content, description)
        )
        self.conn.commit()
        return cursor.lastrowid