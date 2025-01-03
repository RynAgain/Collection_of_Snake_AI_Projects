import SnakeGame from './game.js';

console.log('UI script loaded');

class GameUI {
    constructor() {
        this.game = new SnakeGame();
        this.canvas = document.createElement('canvas');
        this.context = this.canvas.getContext('2d');
        this.canvas.width = 200;
        this.canvas.height = 200;
        document.body.appendChild(this.canvas);
        this.scoreElement = document.createElement('div');
        document.body.appendChild(this.scoreElement);
        this.updateUI();
    }

    updateUI() {
        this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.game.snake.forEach(segment => {
            this.context.fillStyle = 'green';
            this.context.fillRect(segment.x * 20, segment.y * 20, 20, 20);
        });
        this.context.fillStyle = 'red';
        this.context.fillRect(this.game.food.x * 20, this.game.food.y * 20, 20, 20);
        this.scoreElement.innerText = 'Score: ' + this.game.score;
    }

    start() {
        setInterval(() => {
            this.game.update();
            this.updateUI();
        }, 1000 / 10);
    }
}

const gameUI = new GameUI();
gameUI.start();
