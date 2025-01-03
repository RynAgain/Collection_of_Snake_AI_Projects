import Pathfinding from './pathfinding.js';

class SnakeGame {
    constructor() {
        this.snake = [{ x: 5, y: 5 }];
        this.direction = { x: 0, y: 1 };
        this.food = this.generateFood();
        this.score = 0;
        this.pathfinding = new Pathfinding(10);
    }

    generateFood() {
        let newFood;
        do {
            newFood = { x: Math.floor(Math.random() * 10), y: Math.floor(Math.random() * 10) };
        } while (this.snake.some(segment => segment.x === newFood.x && segment.y === newFood.y));
        return newFood;
    }

    update() {
        const path = this.pathfinding.aStar(this.snake[0], this.food, this.snake);
        if (path.length > 1) {
            this.direction = { x: path[1].x - this.snake[0].x, y: path[1].y - this.snake[0].y };
        }

        const head = { x: this.snake[0].x + this.direction.x, y: this.snake[0].y + this.direction.y };
        this.snake.unshift(head);

        if (head.x === this.food.x && head.y === this.food.y) {
            this.score += 10;
            this.food = this.generateFood();
        } else {
            this.snake.pop();
        }

        if (this.isCollision(head)) {
            this.reset();
        }
    }

    isCollision(head) {
        return head.x < 0 || head.x >= 10 || head.y < 0 || head.y >= 10 || this.snake.slice(1).some(segment => segment.x === head.x && segment.y === head.y);
    }

    reset() {
        this.snake = [{ x: 5, y: 5 }];
        this.direction = { x: 0, y: 1 };
        this.food = this.generateFood();
        this.score = 0;
    }
}

export default SnakeGame;
