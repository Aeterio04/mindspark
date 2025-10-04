from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import asyncio
import json
import datetime
import random
from typing import Dict, List, Optional
import uuid

app = FastAPI()

# CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConveyerBelt:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.current_color = None
        self.color_changes = 0
        self.picked_cars = []
        self.sequence_history = []
        
    def find_most_frequent_color(self, buffer_lanes):
        front_colors = {}
        for lane in buffer_lanes:
            for car in lane:
                if car != 0:
                    front_colors[car] = front_colors.get(car, 0) + 1
                    break
        if not front_colors:
            return None
        return max(front_colors.items(), key=lambda x: x[1])[0]
    
    def pick_car(self, buffer_lanes):
        if self.current_color is None:
            self.current_color = self.find_most_frequent_color(buffer_lanes)
            if self.current_color is None:
                return None, -1
        
        for lane_idx, lane in enumerate(buffer_lanes):
            if lane and lane[0] == self.current_color:
                picked_car = lane[0]
                self.picked_cars.append(picked_car)
                self.sequence_history.append({
                    'color': picked_car,
                    'lane': lane_idx,
                    'timestamp': datetime.datetime.now().isoformat(),
                    'color_change': False
                })
                return picked_car, lane_idx
        
        for lane_idx, lane in enumerate(buffer_lanes):
            if lane and lane[0] != 0:
                picked_car = lane[0]
                if picked_car != self.current_color:
                    self.color_changes += 1
                self.current_color = picked_car
                self.picked_cars.append(picked_car)
                self.sequence_history.append({
                    'color': picked_car,
                    'lane': lane_idx,
                    'timestamp': datetime.datetime.now().isoformat(),
                    'color_change': picked_car != self.current_color
                })
                return picked_car, lane_idx
        
        return None, -1

    def get_stats(self):
        stats = {
            'total_picks': len(self.picked_cars),
            'color_changes': self.color_changes,
            
            'current_color': self.current_color,
        }
        if self.picked_cars:
            color_counts = {}
            for car in self.picked_cars:
                color_counts[car] = color_counts.get(car, 0) + 1
            stats['color_distribution'] = color_counts
        return stats

class BufferSystem:
    def __init__(self):
        self.default_color_distribution = {
            'C1': 40, 'C2': 25, 'C3': 12, 'C4': 8, 'C5': 3,
            'C6': 2, 'C7': 2, 'C8': 2, 'C9': 2, 'C10': 2,
            'C11': 2, 'C12': 1, 0: 0
        }
        self.overflow=0
    
        self.reset()
        
    def reset(self):
        self.buffer_lanes = [
            [0] * 14, [0] * 14, [0] * 14, [0] * 14,
            [0] * 16, [0] * 16, [0] * 16, [0] * 16, [0] * 16
        ]
        self.color_distribution = self.default_color_distribution.copy()
        self.conveyer = ConveyerBelt()
        self.cars = 0
        self.penalty_counter = 0
        self.stats = {'total_cars': 0, 'by_color': {}, 'penalties': 0}
        self.operation_log = []
        
    def generate_cars_by_distribution(self, total_cars):
        colors = []
        for color, percentage in self.color_distribution.items():
            if color != 0:
                num_cars = round((percentage / 100) * total_cars)
                colors.extend([color] * num_cars)
        random.shuffle(colors)
        return colors
    
    def update_stats(self, color):
        self.stats['total_cars'] += 1
        self.stats['by_color'][color] = self.stats['by_color'].get(color, 0) + 1
        self.stats['penalties'] = self.penalty_counter
        
    def add_to_bufferline(self, color, oven):
        if oven == 1:
            if self.cars == 0:
                self.buffer_lanes[0][0] = color
                self.cars += 1
                self.update_stats(color)
                self.operation_log.append(f"Added {color} to lane 0 (first car)")
                return True

            lane_color = [next((c for c in lane if c != 0), 0) for lane in self.buffer_lanes[:4]]

            for i in range(4):
                if lane_color[i] == color:
                    for j in range(len(self.buffer_lanes[i])):
                        if self.buffer_lanes[i][j] == 0:
                            self.buffer_lanes[i][j] = color
                            # Record immediately to conveyor visualization
                            self.conveyer.sequence_history.append({
                                'color': color,
                                'lane': i if oven == 1 else 4 + i,
                                'timestamp': datetime.datetime.now().isoformat(),
                                'color_change': False
                            })

                            self.cars += 1
                            self.update_stats(color)
                            self.operation_log.append(f"Added {color} to lane {i} (color match)")
                            return True

            min_priority = float('inf')
            min_lane = 0
            for i in range(4):
                curr_color = lane_color[i]
                priority = self.color_distribution.get(curr_color, float('inf'))
                if priority < min_priority:
                    min_priority = priority
                    min_lane = i

            for j in range(len(self.buffer_lanes[min_lane])):
                if self.buffer_lanes[min_lane][j] == 0:
                    self.buffer_lanes[min_lane][j] = color
                    # Record immediately to conveyor visualization
                    self.conveyer.sequence_history.append({
                        'color': color,
                        'lane': i if oven == 1 else 4 + i,
                        'timestamp': datetime.datetime.now().isoformat(),
                        'color_change': False,
                        
                    })

                    self.cars += 1
                    self.update_stats(color)
                    self.operation_log.append(f"Added {color} to lane {min_lane} (min priority)")
                    return True

            self.penalty_counter += 1
            self.operation_log.append(f"Penalty: {color} overflow to oven 2")
            self.overflow+=1
            return self.add_to_bufferline(color, 2)

        if oven == 2:
            lane_color = [next((c for c in lane if c != 0), 0) for lane in self.buffer_lanes[4:9]]

            for i in range(5):
                if lane_color[i] == color:
                    for j in range(len(self.buffer_lanes[4 + i])):
                        if self.buffer_lanes[4 + i][j] == 0:
                            self.buffer_lanes[4 + i][j] = color
                            self.cars += 1
                            self.update_stats(color)
                            self.operation_log.append(f"Added {color} to lane {4+i} (oven 2 color match)")
                            return True

            min_priority = float('inf')
            min_lane = 4
            for i in range(5):
                curr_color = lane_color[i]
                priority = self.color_distribution.get(curr_color, float('inf'))
                if priority < min_priority:
                    min_priority = priority
                    min_lane = 4 + i

            for j in range(len(self.buffer_lanes[min_lane])):
                if self.buffer_lanes[min_lane][j] == 0:
                    self.buffer_lanes[min_lane][j] = color
                    self.cars += 1
                    self.update_stats(color)
                    self.operation_log.append(f"Added {color} to lane {min_lane} (oven 2 min priority)")
                    return True
            
            self.operation_log.append(f"Error: All lanes full for {color}")
            return False

    def remove_car_from_lane(self, lane_idx):
        if not self.buffer_lanes[lane_idx]:
            return None
        
        car = self.buffer_lanes[lane_idx][0]
        self.buffer_lanes[lane_idx] = self.buffer_lanes[lane_idx][1:] + [0]
        self.cars -= 1
        return car

    def process_conveyer_pickup(self):
        car, lane_idx = self.conveyer.pick_car(self.buffer_lanes)
        if car is not None and lane_idx >= 0:
            self.remove_car_from_lane(lane_idx)
            self.operation_log.append(f"Conveyer picked {car} from lane {lane_idx}")
            return True
        return False

    def get_system_state(self):
        oven1_cars = sum(1 for lane in self.buffer_lanes[:4] for car in lane if car != 0)
        oven2_cars = sum(1 for lane in self.buffer_lanes[4:] for car in lane if car != 0)
        oven1_capacity = sum(len(lane) for lane in self.buffer_lanes[:4])
        oven2_capacity = sum(len(lane) for lane in self.buffer_lanes[4:])
        
        conveyer_stats = self.conveyer.get_stats()
        buffer_stats=self.overflow
        
        return {
            'buffer_lanes': {
                'oven1': [
                    {
                        'id': f'L{i+1}',
                        'capacity': len(lane),
                        'current': sum(1 for car in lane if car != 0),
                        'vehicles': [car for car in lane if car != 0],
                        'status': self.get_lane_status(lane)
                    } for i, lane in enumerate(self.buffer_lanes[:4])
                ],
                'oven2': [
                    {
                        'id': f'L{i+5}',
                        'capacity': len(lane),
                        'current': sum(1 for car in lane if car != 0),
                        'vehicles': [car for car in lane if car != 0],
                        'status': self.get_lane_status(lane)
                    } for i, lane in enumerate(self.buffer_lanes[4:9])
                ]
            },
            'conveyer': {
                'current_color': conveyer_stats['current_color'],
                'total_picks': conveyer_stats['total_picks'],
                'color_changes': conveyer_stats['color_changes'],
                'recent_sequence': [item['color'] for item in self.conveyer.sequence_history[-20:]],  # Last 20 picks
                
            },
            'kpis': {
                'throughput': conveyer_stats['total_picks'],
                'targetJPH': 900,
                'colorChangeovers': conveyer_stats['color_changes'],
                'bufferUtilization': round((oven1_cars + oven2_cars) / (oven1_capacity + oven2_capacity) * 100),
                'ovenEfficiency': 94.2,
                'totalVehicles': self.stats['total_cars'],'overflowPenalties' : buffer_stats,
            },
            'stats': {
                'oven1_utilization': round(oven1_cars/oven1_capacity * 100, 1),
                'oven2_utilization': round(oven2_cars/oven2_capacity * 100, 1),
                'total_cars': self.stats['total_cars'],
                'penalties': self.stats['penalties'],
                'color_distribution': self.stats['by_color']
            }
        }
    
    def get_lane_status(self, lane):
        filled = sum(1 for car in lane if car != 0)
        capacity = len(lane)
        utilization = filled / capacity
        
        if utilization >= 0.9:
            return 'critical'
        elif utilization >= 0.7:
            return 'warning'
        else:
            return 'active'

class SimulationManager:
    def __init__(self):
        self.buffer_system = BufferSystem()
        self.is_running = False
        self.simulation_speed = 1.0  # seconds between operations
        
    async def run_simulation(self, websocket):
        self.is_running = True
        self.buffer_system.reset()
        
        # Generate initial batch of cars
        colors = self.buffer_system.generate_cars_by_distribution(50)
        
        color_index = 0
        operation_count = 0
        
        while self.is_running and color_index < len(colors):
            try:
                # Alternate between adding cars and processing conveyer
                if operation_count % 3 != 0:  # Add cars more frequently
                    if color_index < len(colors):
                        color = colors[color_index]
                        oven = 1 if color_index % 2 == 0 else 2
                        self.buffer_system.add_to_bufferline(color, oven)
                        color_index += 1
                else:  # Process conveyer pickup
                    self.buffer_system.process_conveyer_pickup()
                
                # Send updated state to frontend
                state = self.buffer_system.get_system_state()
                await websocket.send_json({
                    'type': 'system_update',
                    'data': state
                })
                
                operation_count += 1
                await asyncio.sleep(self.simulation_speed)
                
            except Exception as e:
                print(f"Simulation error: {e}")
                break
        
        self.is_running = False
    
    def stop_simulation(self):
        self.is_running = False

simulation_manager = SimulationManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message['type'] == 'start_simulation':
                asyncio.create_task(simulation_manager.run_simulation(websocket))
                
            elif message['type'] == 'stop_simulation':
                simulation_manager.stop_simulation()
                
            elif message['type'] == 'reset_system':
                simulation_manager.buffer_system.reset()
                state = simulation_manager.buffer_system.get_system_state()
                await websocket.send_json({
                    'type': 'system_update',
                    'data': state
                })
                
            elif message['type'] == 'update_speed':
                simulation_manager.simulation_speed = message['speed']
                
    except WebSocketDisconnect:
        simulation_manager.stop_simulation()
        print("Client disconnected")

@app.get("/")
async def get():
    return HTMLResponse("""
    <html>
        <head>
            <title>Conveyor Sequencing Backend</title>
        </head>
        <body>
            <h1>Conveyor Sequencing System Backend</h1>
            <p>WebSocket endpoint is available at /ws</p>
            <p>Connect your frontend to visualize the conveyor sequencing system.</p>
        </body>
    </html>
    """)

@app.get("/api/system-state")
async def get_system_state():
    return simulation_manager.buffer_system.get_system_state()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)