import tkinter as tk
import math
import sys
import os

# Añadir el directorio src al path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', 'src')
sys.path.insert(0, src_dir)

try:
    from utils.constants import Constants
except ImportError:
    # Si falla, definir constantes aquí
    class Constants:
        CANVAS_MARGIN = 50

class StarCanvas(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.graph = None
        self.control_panel = None
        self.star_objects = {}
        self.connection_objects = {}
        self.scale_factor = 1.0
        self.offset_x = 50
        self.offset_y = 50
        self.obstacle_mode = False
        self.burro_id = None
        self.current_route = []
        self.current_step = 0
        
        self.bind("<Configure>", self.on_resize)
        self.bind("<Button-1>", self.on_click)
        self.bind("<Button-3>", self.on_right_click)
        self.bind("<Motion>", self.on_motion)
    
    def on_resize(self, event):
        self.calculate_scale_factor()
        if self.graph:
            self.draw_graph(self.graph)
    
    def calculate_scale_factor(self):
        canvas_width = self.winfo_width() - 2 * self.offset_x
        canvas_height = self.winfo_height() - 2 * self.offset_y
        
        if canvas_width > 0 and canvas_height > 0:
            self.scale_x = canvas_width / 200.0
            self.scale_y = canvas_height / 200.0
            self.scale_factor = min(self.scale_x, self.scale_y)
    
    def draw_graph(self, graph):
        self.graph = graph
        self.delete("all")
        self.star_objects.clear()
        self.connection_objects.clear()
        
        self.calculate_scale_factor()
        self.draw_connections()
        self.draw_stars()
    
    def draw_connections(self):
        if not self.graph or not self.graph.constellations:
            return
            
        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]
        
        for i, constellation in enumerate(self.graph.constellations):
            color = colors[i % len(colors)]
            
            for star in constellation.stars:
                x1, y1 = self.transform_coordinates(star.coordinates['x'], star.coordinates['y'])
                
                for connection in star.linked_to:
                    connected_star = self.graph.get_star_by_id(connection['starId'])
                    if connected_star:
                        x2, y2 = self.transform_coordinates(
                            connected_star.coordinates['x'], 
                            connected_star.coordinates['y']
                        )
                        
                        line_width = 2
                        line_color = color
                        dash_pattern = None
                        
                        if self.graph.is_edge_blocked(star.id, connected_star.id):
                            line_color = "red"
                            dash_pattern = (5, 2)
                            line_width = 3
                        
                        line_id = self.create_line(
                            x1, y1, x2, y2,
                            width=line_width,
                            fill=line_color,
                            dash=dash_pattern,
                            tags="connection"
                        )
                        
                        key = tuple(sorted([star.id, connected_star.id]))
                        self.connection_objects[key] = {
                            'line_id': line_id,
                            'star1': star.id,
                            'star2': connected_star.id
                        }
    
    def draw_stars(self):
        if not self.graph:
            return
            
        coordinate_groups = {}
        for star in self.graph.get_all_stars():
            coord_key = (star.coordinates['x'], star.coordinates['y'])
            if coord_key not in coordinate_groups:
                coordinate_groups[coord_key] = []
            coordinate_groups[coord_key].append(star)
        
        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]
        
        for i, constellation in enumerate(self.graph.constellations):
            color = colors[i % len(colors)]
            
            for star in constellation.stars:
                x, y = self.transform_coordinates(star.coordinates['x'], star.coordinates['y'])
                
                base_radius = 8
                scaled_radius = base_radius + (star.radius * 10)
                
                fill_color = color
                coord_key = (star.coordinates['x'], star.coordinates['y'])
                if len(coordinate_groups[coord_key]) > 1:
                    fill_color = "red"
                    scaled_radius += 3
                
                if star.hypergiant:
                    scaled_radius *= 1.8
                    outline_color = "gold"
                    outline_width = 3
                else:
                    outline_color = "black"
                    outline_width = 2
                
                scaled_radius = max(scaled_radius, 6)
                
                star_id = self.create_oval(
                    x - scaled_radius, y - scaled_radius,
                    x + scaled_radius, y + scaled_radius,
                    fill=fill_color,
                    outline=outline_color,
                    width=outline_width,
                    tags=f"star_{star.id}"
                )
                
                label_id = self.create_text(
                    x, y - scaled_radius - 12,
                    text=f"{star.label} (ID:{star.id})",
                    font=("Arial", 8),
                    tags=f"label_{star.id}"
                )
                
                self.star_objects[star.id] = {
                    'circle': star_id,
                    'label': label_id,
                    'x': x,
                    'y': y,
                    'radius': scaled_radius
                }
    
    def transform_coordinates(self, x, y):
        canvas_x = self.offset_x + (x * self.scale_factor)
        canvas_y = self.offset_y + (y * self.scale_factor)
        return canvas_x, canvas_y
    
    def on_click(self, event):
        if self.obstacle_mode:
            connection = self.find_connection_at_position(event.x, event.y)
            if connection:
                self.toggle_connection_block(connection)
        else:
            clicked_star = self.find_star_at_position(event.x, event.y)
            if clicked_star:
                self.highlight_star(clicked_star, "green")
                if self.control_panel:
                    self.control_panel.set_selected_star(clicked_star, False)
    
    def on_right_click(self, event):
        if not self.obstacle_mode:
            clicked_star = self.find_star_at_position(event.x, event.y)
            if clicked_star:
                self.highlight_star(clicked_star, "blue")
                if self.control_panel:
                    self.control_panel.set_selected_star(clicked_star, True)
    
    def on_motion(self, event):
        if self.obstacle_mode:
            connection = self.find_connection_at_position(event.x, event.y)
            if connection:
                self.config(cursor="hand2")
            else:
                self.config(cursor="")
        else:
            self.config(cursor="")
    
    def find_star_at_position(self, x, y, tolerance=15):
        for star_id, star_data in self.star_objects.items():
            distance = math.sqrt((star_data['x'] - x)**2 + (star_data['y'] - y)**2)
            if distance <= tolerance:
                return star_id
        return None
    
    def find_connection_at_position(self, x, y, tolerance=8):
        for connection_data in self.connection_objects.values():
            star1 = self.graph.get_star_by_id(connection_data['star1'])
            star2 = self.graph.get_star_by_id(connection_data['star2'])
            
            if star1 and star2:
                x1, y1 = self.transform_coordinates(star1.coordinates['x'], star1.coordinates['y'])
                x2, y2 = self.transform_coordinates(star2.coordinates['x'], star2.coordinates['y'])
                
                distance = self.point_to_line_distance(x, y, x1, y1, x2, y2)
                if distance <= tolerance:
                    return connection_data
        return None
    
    def point_to_line_distance(self, px, py, x1, y1, x2, y2):
        line_vec = (x2 - x1, y2 - y1)
        point_vec = (px - x1, py - y1)
        
        line_len_squared = line_vec[0]**2 + line_vec[1]**2
        
        if line_len_squared == 0:
            return math.sqrt(point_vec[0]**2 + point_vec[1]**2)
        
        t = max(0, min(1, (point_vec[0]*line_vec[0] + point_vec[1]*line_vec[1]) / line_len_squared))
        
        projection = (x1 + t * line_vec[0], y1 + t * line_vec[1])
        
        return math.sqrt((px - projection[0])**2 + (py - projection[1])**2)
    
    def toggle_connection_block(self, connection_data):
        star1_id = connection_data['star1']
        star2_id = connection_data['star2']
        
        if self.graph.is_edge_blocked(star1_id, star2_id):
            self.graph.unblock_edge(star1_id, star2_id)
        else:
            self.graph.block_edge(star1_id, star2_id)
        
        self.draw_connection(connection_data)
    
    def draw_connection(self, connection_data):
        star1 = self.graph.get_star_by_id(connection_data['star1'])
        star2 = self.graph.get_star_by_id(connection_data['star2'])
        
        if star1 and star2:
            x1, y1 = self.transform_coordinates(star1.coordinates['x'], star1.coordinates['y'])
            x2, y2 = self.transform_coordinates(star2.coordinates['x'], star2.coordinates['y'])
            
            colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]
            constellation = self.graph.get_constellation_for_star(star1.id)
            color = colors[0]  # Color por defecto
            
            if constellation and self.graph.constellations:
                try:
                    index = self.graph.constellations.index(constellation)
                    color = colors[index % len(colors)]
                except:
                    pass
            
            line_width = 2
            dash_pattern = None
            
            if self.graph.is_edge_blocked(star1.id, star2.id):
                color = "red"
                dash_pattern = (5, 2)
                line_width = 3
            
            self.itemconfig(connection_data['line_id'], 
                          fill=color, 
                          dash=dash_pattern,
                          width=line_width)
    
    def highlight_star(self, star_id, color="yellow"):
        if star_id in self.star_objects:
            star_data = self.star_objects[star_id]
            self.itemconfig(star_data['circle'], outline=color, width=4)
    
    def highlight_route(self, route):
        self.reset_highlight()
        self.current_route = route
        
        if not route:
            return
        
        for i, star_id in enumerate(route):
            if star_id in self.star_objects:
                star_data = self.star_objects[star_id]
                color = "green" if i == 0 else "blue" if i == len(route)-1 else "orange"
                self.itemconfig(star_data['circle'], outline=color, width=4)
        
        for i in range(len(route) - 1):
            star1_id, star2_id = route[i], route[i+1]
            key = tuple(sorted([star1_id, star2_id]))
            if key in self.connection_objects:
                connection_data = self.connection_objects[key]
                self.itemconfig(connection_data['line_id'], fill="green", width=4)
    
    def draw_burro(self, x, y):
        self.delete("burro")
        
        burro_radius = 6
        self.burro_id = self.create_oval(
            x - burro_radius, y - burro_radius,
            x + burro_radius, y + burro_radius,
            fill="brown", outline="black", width=2,
            tags="burro"
        )
        
        ear_radius = 3
        self.create_oval(
            x - burro_radius - 2, y - burro_radius - 2,
            x - burro_radius + ear_radius, y - burro_radius + ear_radius,
            fill="brown", outline="black", width=1,
            tags="burro"
        )
        self.create_oval(
            x + burro_radius - ear_radius, y - burro_radius - 2,
            x + burro_radius + 2, y - burro_radius + ear_radius,
            fill="brown", outline="black", width=1,
            tags="burro"
        )
    
    def animate_journey(self, route, speed=500):
        if not route:
            return
        
        self.current_step = 0
        self.animate_step(route, speed)
    
    def animate_step(self, route, speed):
        if self.current_step >= len(route):
            return
        
        current_star_id = route[self.current_step]
        if current_star_id in self.star_objects:
            star_data = self.star_objects[current_star_id]
            self.draw_burro(star_data['x'], star_data['y'])
            
            if self.control_panel and hasattr(self.control_panel, 'route_text'):
                star = self.graph.get_star_by_id(current_star_id)
                if star:
                    info = f"Visitando: {star.label}\nPaso: {self.current_step + 1}/{len(route)}"
                    self.control_panel.route_text.config(state=tk.NORMAL)
                    self.control_panel.route_text.insert(tk.END, f"\n{info}")
                    self.control_panel.route_text.see(tk.END)
                    self.control_panel.route_text.config(state=tk.DISABLED)
        
        self.current_step += 1
        
        if self.current_step < len(route):
            self.after(speed, lambda: self.animate_step(route, speed))
    
    def reset_highlight(self):
        for star_data in self.star_objects.values():
            self.itemconfig(star_data['circle'], outline="black", width=2)
        
        for connection_data in self.connection_objects.values():
            self.draw_connection(connection_data)