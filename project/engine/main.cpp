#include <iostream>
#include <fstream>
#include <vector>
#include "json.hpp"
#include "linked_list.cpp"
#include "tree.cpp"

using json = nlohmann::json;

// Grid dimensions
int ROWS, COLS;

// Wall grid
bool walls[100][100];

// Pheromone grid
float pheromones[100][100];

// Direction vectors: up, down, left, right
int dx[] = {0, 0, -1, 1};
int dy[] = {-1, 1, 0, 0};

struct Candidate {
    int x, y;
    float pheromone;
};

// Get valid neighbors (not wall, not visited)
std::vector<Candidate> getNeighbors(int x, int y, AVLTree& visited) {
    std::vector<Candidate> candidates;
    for (int i = 0; i < 4; i++) {
        int nx = x + dx[i];
        int ny = y + dy[i];
        if (nx < 0 || ny < 0 || nx >= COLS || ny >= ROWS) continue;
        if (walls[ny][nx]) continue;
        if (visited.isVisited(nx, ny)) continue;
        candidates.push_back({nx, ny, pheromones[ny][nx]});
    }
    // Sort by pheromone descending (greedy)
    for (int i = 0; i < (int)candidates.size() - 1; i++)
        for (int j = i + 1; j < (int)candidates.size(); j++)
            if (candidates[j].pheromone > candidates[i].pheromone)
                std::swap(candidates[i], candidates[j]);
    return candidates;
}

// Backtracking + Greedy
// Returns true if path to home was found
bool solve(int x, int y, int hx, int hy, PathStack& path, AVLTree& visited) {
    // Mark current as visited
    visited.insertNode(x, y, pheromones[y][x]);

    // Base case: reached home
    if (x == hx && y == hy) return true;

    // Get neighbors sorted by pheromone (greedy order)
    std::vector<Candidate> neighbors = getNeighbors(x, y, visited);

    for (auto& c : neighbors) {
        path.push(c.x, c.y);
        if (solve(c.x, c.y, hx, hy, path, visited))
            return true;
        path.pop(); // Backtrack
    }

    return false; // Dead end
}

int main(){
    // Read input.json
    std::ifstream fileIn("input.json");
    if (!fileIn.is_open()){
        std::cerr << "Error: could not open input.json" << std::endl;
        return 1;
    }
    json input;
    try {
        fileIn >> input;
    } catch (const nlohmann::json::parse_error& e){
        std::cerr << "Error parsing input.json: " << e.what() << std::endl;
        return 1;
    }
    fileIn.close();

    // Load grid config
    COLS = input["grid_size"][0];
    ROWS = input["grid_size"][1];

    int startX = input["ant_pos"][0];
    int startY = input["ant_pos"][1];
    int homeX  = input["home_pos"][0];
    int homeY  = input["home_pos"][1];

    // Initialize grids
    for (int i = 0; i < ROWS; i++)
        for (int j = 0; j < COLS; j++) {
            walls[i][j]     = false;
            pheromones[i][j] = 0.0f;
        }

    // Load walls
    for (auto& w : input["walls"])
        walls[(int)w[1]][(int)w[0]] = true;

    // Load pheromones
    for (auto it = input["pheromones"].items().begin(); it != input["pheromones"].items().end(); ++it) {
        std::string key = it.key();
        float val = it.value();
        int px, py;
        sscanf(key.c_str(), "%d,%d", &px, &py);
        pheromones[py][px] = val;
    }

    // Run algorithm
    PathStack path;
    AVLTree   visited;

    path.push(startX, startY);
    bool found = solve(startX, startY, homeX, homeY, path, visited);

    // Build output path array (stack is LIFO, collect then reverse)
    std::vector<std::pair<int,int>> pathVec;
    while (!path.isEmpty()) {
        Coord c = path.pop();
        pathVec.push_back({c.x, c.y});
    }
    std::reverse(pathVec.begin(), pathVec.end());

    // Write state.json
    json output;
    output["status"] = found ? "Success" : "No path";

    json pathArr = json::array();
    for (auto& p : pathVec)
        pathArr.push_back({p.first, p.second});
    output["path"] = pathArr;

    if (!pathVec.empty())
        output["current_pos"] = {pathVec.back().first, pathVec.back().second};
    else
        output["current_pos"] = {startX, startY};

    std::ofstream fileOut("state.json");
    fileOut << output.dump(4);
    fileOut.close();

    std::cout << (found ? "Path found!" : "No path found.") << std::endl;
    return 0;
}
