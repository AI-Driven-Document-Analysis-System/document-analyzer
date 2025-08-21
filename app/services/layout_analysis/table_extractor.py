class TableExtractor:
    """Extract and process tabular data from documents"""
    
    def __init__(self):
        self.setup_table_detection()
    
    def setup_table_detection(self):
        """Setup table detection capabilities"""
        # This would typically use TableNet or similar models
        # For now, we'll use a simplified approach
        self.table_detector_available = False
        logger.info("Table extraction initialized with rule-based detection")
    
    def detect_tables_rule_based(self, image: np.ndarray, layout_elements: List[Dict]) -> List[Dict[str, Any]]:
        """Detect tables using rule-based approach"""
        # Simple table detection based on aligned text elements
        tables = []
        
        # Group elements that might form a table
        potential_table_elements = []
        
        for element in layout_elements:
            bbox = element['bounding_box']
            # Look for elements that might be in tabular format
            if self.is_potential_table_element(element):
                potential_table_elements.append(element)
        
        if len(potential_table_elements) < 4:  # Minimum elements for a table
            return tables
        
        # Group by proximity and alignment
        table_groups = self.group_table_elements(potential_table_elements)
        
        for group in table_groups:
            if len(group) >= 4:  # Minimum cells for a table
                table_bbox = self.calculate_table_bbox(group)
                table_data = self.extract_table_structure(group)
                
                tables.append({
                    'bounding_box': table_bbox,
                    'element_type': 'table',
                    'confidence': 0.8,
                    'extracted_text': self.format_table_text(table_data),
                    'metadata': {
                        'table_structure': table_data,
                        'cell_count': len(group)
                    }
                })
        
        return tables
    
    def is_potential_table_element(self, element: Dict) -> bool:
        """Check if an element might be part of a table"""
        text = element['text'].strip()
        
        # Check for numeric content, short text, or specific patterns
        if not text:
            return False
        
        # Elements with numbers, currency, or short text might be table cells
        if (any(char.isdigit() for char in text) or 
            len(text.split()) <= 3 or
            any(symbol in text for symbol in ['$', '%', '€', '£'])):
            return True
        
        return False
    
    def group_table_elements(self, elements: List[Dict]) -> List[List[Dict]]:
        """Group elements that might belong to the same table"""
        if not elements:
            return []
        
        # Sort by vertical position
        elements.sort(key=lambda x: (x['bounding_box'][1], x['bounding_box'][0]))
        
        groups = []
        current_group = [elements[0]]
        
        for i in range(1, len(elements)):
            current_bbox = elements[i]['bounding_box']
            prev_bbox = elements[i-1]['bounding_box']
            
            # Check vertical distance
            vertical_distance = current_bbox[1] - prev_bbox[3]
            
            # If elements are close vertically, they might be in the same table
            if vertical_distance < 100:  # Threshold for table grouping
                current_group.append(elements[i])
            else:
                if len(current_group) >= 4:
                    groups.append(current_group)
                current_group = [elements[i]]
        
        # Add the last group
        if len(current_group) >= 4:
            groups.append(current_group)
        
        return groups
    
    def calculate_table_bbox(self, elements: List[Dict]) -> List[int]:
        """Calculate bounding box for entire table"""
        if not elements:
            return [0, 0, 0, 0]
        
        min_x = min(elem['bounding_box'][0] for elem in elements)
        min_y = min(elem['bounding_box'][1] for elem in elements)
        max_x = max(elem['bounding_box'][2] for elem in elements)
        max_y = max(elem['bounding_box'][3] for elem in elements)
        
        return [min_x, min_y, max_x, max_y]
    
    def extract_table_structure(self, elements: List[Dict]) -> Dict[str, Any]:
        """Extract table structure from grouped elements"""
        # Sort elements by position (row-wise)
        sorted_elements = sorted(elements, key=lambda x: (x['bounding_box'][1], x['bounding_box'][0]))
        
        # Determine rows and columns
        rows = []
        current_row = []
        current_y = sorted_elements[0]['bounding_box'][1]
        row_threshold = 20
        
        for element in sorted_elements:
            bbox = element['bounding_box']
            
            if abs(bbox[1] - current_y) < row_threshold:
                current_row.append(element)
            else:
                if current_row:
                    # Sort row elements by x position
                    current_row.sort(key=lambda x: x['bounding_box'][0])
                    rows.append(current_row)
                current_row = [element]
                current_y = bbox[1]
        
        # Add last row
        if current_row:
            current_row.sort(key=lambda x: x['bounding_box'][0])
            rows.append(current_row)
        
        # Extract text content
        table_data = []
        for row in rows:
            row_data = [elem['text'] for elem in row]
            table_data.append(row_data)
        
        return {
            'rows': len(rows),
            'max_columns': max(len(row) for row in rows) if rows else 0,
            'data': table_data
        }
    
    def format_table_text(self, table_data: Dict[str, Any]) -> str:
        """Format table data as readable text"""
        if not table_data.get('data'):
            return ""
        
        formatted_text = "Table:\n"
        for i, row in enumerate(table_data['data']):
            formatted_text += f"Row {i+1}: " + " | ".join(row) + "\n"
        
        return formatted_text.strip()
    
    def extract_tables(self, image: np.ndarray, layout_elements: List[Dict]) -> List[Dict[str, Any]]:
        """Main table extraction method"""
        return self.detect_tables_rule_based(image, layout_elements)
