class Pathfinding {
    constructor(gridSize) {
        this.gridSize = gridSize;
        this.hamiltonianCycle = this.createHamiltonianCycle();
    }

    createHamiltonianCycle() {
        const cycle = [];
        for (let y = 0; y < this.gridSize; y++) {
            if (y % 2 === 0) {
                for (let x = 0; x < this.gridSize; x++) {
                    cycle.push({ x, y });
                }
            } else {
                for (let x = this.gridSize - 1; x >= 0; x--) {
                    cycle.push({ x, y });
                }
            }
        }
        // Ensure the cycle is complete and covers all grid points
        if (cycle.length !== this.gridSize * this.gridSize) {
            throw new Error("Hamiltonian cycle is incomplete.");
        }
        return cycle;
    }

    aStar(start, goal, snake) {
        const pathToFood = this.findPathToFood(start, goal, snake);
        if (pathToFood.length > 0) {
            return pathToFood;
        }
        return this.followHamiltonianCycle(start, snake);
    }

    findPathToFood(start, goal, snake) {
        const openSet = [start];
        const cameFrom = new Map();
        const gScore = new Map();
        const fScore = new Map();

        gScore.set(this.hash(start), 0);
        fScore.set(this.hash(start), this.heuristic(start, goal));

        while (openSet.length > 0) {
            openSet.sort((a, b) => fScore.get(this.hash(a)) - fScore.get(this.hash(b)));
            const current = openSet.shift();

            if (current.x === goal.x && current.y === goal.y) {
                return this.reconstructPath(cameFrom, current);
            }

            for (const neighbor of this.getNeighbors(current, snake)) {
                const tentativeGScore = gScore.get(this.hash(current)) + 1;

                if (tentativeGScore < (gScore.get(this.hash(neighbor)) || Infinity)) {
                    cameFrom.set(this.hash(neighbor), current);
                    gScore.set(this.hash(neighbor), tentativeGScore);
                    fScore.set(this.hash(neighbor), tentativeGScore + this.heuristic(neighbor, goal));

                    if (!openSet.some(n => n.x === neighbor.x && n.y === neighbor.y)) {
                        openSet.push(neighbor);
                    }
                }
            }
        }

        return [];
    }

    followHamiltonianCycle(start, snake) {
        const currentIndex = this.hamiltonianCycle.findIndex(node => node.x === start.x && node.y === start.y);
        const nextIndex = (currentIndex + 1) % this.hamiltonianCycle.length;
        return [start, this.hamiltonianCycle[nextIndex]];
    }

    heuristic(a, b) {
        return Math.abs(a.x - b.x) + Math.abs(a.y - b.y);
    }

    getNeighbors(node, snake) {
        const directions = [
            { x: 1, y: 0 },
            { x: -1, y: 0 },
            { x: 0, y: 1 },
            { x: 0, y: -1 }
        ];

        return directions.map(dir => ({ x: node.x + dir.x, y: node.y + dir.y }))
            .filter(neighbor => this.isValid(neighbor, snake));
    }

    isValid(node, snake) {
        return node.x >= 0 && node.x < this.gridSize && node.y >= 0 && node.y < this.gridSize &&
            !snake.some(segment => segment.x === node.x && segment.y === node.y);
    }

    hash(node) {
        return `${node.x},${node.y}`;
    }

    reconstructPath(cameFrom, current) {
        const totalPath = [current];
        while (cameFrom.has(this.hash(current))) {
            current = cameFrom.get(this.hash(current));
            totalPath.unshift(current);
        }
        return totalPath;
    }
}

export default Pathfinding;
