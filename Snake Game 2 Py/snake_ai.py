import numpy as np
import random
from collections import deque
import torch
import torch.nn as nn
import torch.optim as optim

class ReplayBuffer:
    def __init__(self, max_size):
        self.buffer = deque(maxlen=max_size)

    def add(self, experience):
        self.buffer.append(experience)

    def sample(self, batch_size):
        return random.sample(self.buffer, batch_size)

    def size(self):
        return len(self.buffer)

class DQNSnakeAI:
    def __init__(self, state_size, action_size, max_moves):
        self.state_size = state_size  # (width, height)
        self.action_size = action_size
        self.max_moves = max_moves  # Maximum possible moves on the board
        self.memory = ReplayBuffer(max_size=5000)
        self.gamma = 0.95  # Discount factor
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.batch_size = 64
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._build_model().to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.criterion = nn.MSELoss()

    def _build_model(self):
        input_dim = 11  # Updated state size
        class Net(nn.Module):
            def __init__(self, input_dim, output_dim):
                super(Net, self).__init__()
                self.fc1 = nn.Linear(input_dim, 128)
                self.fc2 = nn.Linear(128, 128)
                self.fc3 = nn.Linear(128, output_dim)

                nn.init.xavier_uniform_(self.fc1.weight)
                nn.init.xavier_uniform_(self.fc2.weight)
                nn.init.xavier_uniform_(self.fc3.weight)

            def forward(self, x):
                x = torch.relu(self.fc1(x))
                x = torch.relu(self.fc2(x))
                x = self.fc3(x)
                return x

        return Net(input_dim=input_dim, output_dim=self.action_size)

    def get_state(self, snake_head, snake_body, food_pos):
        # Direction vectors
        direction = self.get_direction_vector(snake_body)

        dir_left = direction == (-10, 0)
        dir_right = direction == (10, 0)
        dir_up = direction == (0, -10)
        dir_down = direction == (0, 10)

        # Danger variables
        danger_straight = self.check_collision(snake_head, snake_body, self.state_size, action="STRAIGHT")
        danger_right = self.check_collision(snake_head, snake_body, self.state_size, action="RIGHT")
        danger_left = self.check_collision(snake_head, snake_body, self.state_size, action="LEFT")

        # Food location
        food_left = food_pos[0] < snake_head[0]
        food_right = food_pos[0] > snake_head[0]
        food_up = food_pos[1] < snake_head[1]
        food_down = food_pos[1] > snake_head[1]

        state = [
            int(danger_straight),
            int(danger_right),
            int(danger_left),
            int(dir_left),
            int(dir_right),
            int(dir_up),
            int(dir_down),
            int(food_left),
            int(food_right),
            int(food_up),
            int(food_down)
        ]

        return np.array(state, dtype=int)

    def get_direction_vector(self, body):
        if len(body) >= 2:
            x1, y1 = body[-1]
            x2, y2 = body[-2]
            return (x1 - x2, y1 - y2)
        else:
            # Default direction (moving right)
            return (10, 0)

    def check_collision(self, head, body, state_size, action):
        x, y = head
        if action == "STRAIGHT":
            x_change, y_change = self.get_direction_vector(body)
        elif action == "RIGHT":
            x_change, y_change = self.turn_right(self.get_direction_vector(body))
        elif action == "LEFT":
            x_change, y_change = self.turn_left(self.get_direction_vector(body))

        next_pos = (x + x_change, y + y_change)

        if next_pos[0] < 0 or next_pos[0] >= state_size[0] * 10 or next_pos[1] < 0 or next_pos[1] >= state_size[1] * 10:
            return True  # Collision with wall
        for segment in body:
            if next_pos == segment:
                return True  # Collision with self
        return False

    def turn_right(self, direction):
        x, y = direction
        return (y, -x)

    def turn_left(self, direction):
        x, y = direction
        return (-y, x)

    def choose_action(self, state, snake_length):
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        if np.random.rand() <= self.epsilon:
            safe_actions = self.plan_ahead(state, snake_length)
            return random.choice(safe_actions)
        with torch.no_grad():
            act_values = self.model(state_tensor)
        best_action = torch.argmax(act_values).item()
        safe_actions = self.plan_ahead(state, snake_length)
        if best_action in safe_actions:
            return best_action
        else:
            return random.choice(safe_actions)

    def plan_ahead(self, state, snake_length):
        depth = min(snake_length ** 3, self.max_moves)
        return self.recursive_search(state, depth)

    def recursive_search(self, state, depth):
        safe_actions = []
        for action in range(self.action_size):
            if not self.check_future_collision(state, action, depth):
                safe_actions.append(action)
        return safe_actions if safe_actions else [0, 1, 2, 3]

    def check_future_collision(self, state, action, depth):
        if depth == 0:
            return False
        # Simulate the action and check for collision recursively
        # This requires a simulation of the game environment which is complex
        # For simplicity, we'll assume that the immediate move determines safety
        danger = state[action]
        if danger:
            return True
        else:
            return False

    def learn(self):
        if self.memory.size() < self.batch_size:
            return
        minibatch = self.memory.sample(self.batch_size)
        states, actions, rewards, next_states, dones = zip(*minibatch)

        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).unsqueeze(1).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)

        current_q = self.model(states).gather(1, actions).squeeze(1)
        max_next_q = self.model(next_states).max(1)[0]
        expected_q = rewards + (1 - dones) * self.gamma * max_next_q

        loss = self.criterion(current_q, expected_q.detach())
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def remember(self, state, action, reward, next_state, done):
        self.memory.add((state, action, reward, next_state, done))

    def save_model(self, filename='dqn_snake_ai_model.pth'):
        torch.save(self.model.state_dict(), filename)

    def load_model(self, filename='dqn_snake_ai_model.pth'):
        try:
            self.model.load_state_dict(torch.load(filename))
            self.model.to(self.device)
        except FileNotFoundError:
            print("Model file not found. Starting with a new model.")

    def evaluate(self, episode):
        if episode % 20 == 0:
            print(f"Evaluating at episode {episode}")
            # Implement evaluation logic here
            pass
