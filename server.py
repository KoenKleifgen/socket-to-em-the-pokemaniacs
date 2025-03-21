import socket
import json
import threading
import random
import pygame
from game import Game, Player
from map import generate_map 

clients = []
clients_lock = threading.Lock()

def is_valid_spawn(game_map, x, y):
    """Checks if the given coordinates are a valid spawn position (black cell)."""
    if 0 <= y < len(game_map) and 0 <= x < len(game_map[0]):
        return game_map[y][x] == 0
    return True

def handle_client(conn, client_id, client_player):
    buffer = ""
    try:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            buffer += data
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                try:
                    msg = json.loads(line)
                    if msg["type"] == "pos":
                        pos = msg["data"]
                        client_player.x = pos["x"]
                        client_player.y = pos["y"]
                except Exception as e:
                    print(f"Error processing message from client {client_id}: {e}")
    except Exception as e:
        print(f"Client {client_id} connection error: {e}")
    finally:
        print(f"Client {client_id} disconnected")
        conn.close()
        with clients_lock:
            for i, (cid, _, _) in enumerate(clients):
                if cid == client_id:
                    clients.pop(i)
                    break

def broadcast_state(game, server_player):
    with clients_lock:
        state = {
            "type": "state",
            "data": {
                "server": {
                    "id": "server",
                    "x": server_player.x,
                    "y": server_player.y,
                    "role": server_player.role
                },
                "clients": {
                    str(cid): {
                        "id": str(cid),
                        "x": pl.x,
                        "y": pl.y,
                        "role": pl.role
                    } for cid, pl, _ in clients
                }
            }
        }
        msg = (json.dumps(state) + "\n").encode()
        for _, _, conn in clients:
            try:
                conn.sendall(msg)
            except Exception as e:
                print("Error sending state to a client:", e)




def check_tagging(game):
    tagger = None
    with clients_lock:
        for cid, pl, _ in clients:
            if pl.role == "tagger":
                tagger = pl
                break
    if tagger:
        # Check all clients.
        with clients_lock:
            for cid, pl, _ in clients:
                if pl.role == "runner" and abs(tagger.x - pl.x) < 0.5 and abs(tagger.y - pl.y) < 0.5:
                    pl.role = "tagged"
        # Check the server's local player.
        if game.local_player.role == "runner" and abs(tagger.x - game.local_player.x) < 0.5 and abs(tagger.y - game.local_player.y) < 0.5:
            game.local_player.role = "tagged"

def accept_clients(server_socket, game, used_spawns):
    """Continuously accepts new clients and assigns them a spawn."""
    client_id_counter = 1
    tagger_assigned = False  # Flag to ensure only one tagger

    while True:
        conn, addr = server_socket.accept()
        print(f"Client {client_id_counter} connected: {addr}")
        # Send the map so the client can initialize its game state.
        map_msg = json.dumps({"type": "map", "data": game.game_map}) + "\n"
        try:
            conn.sendall(map_msg.encode())
        except Exception as e:
            print("Error sending map:", e)
            conn.close()
            continue

        # Send the client ID
        id_msg = json.dumps({"type": "client_id", "data": client_id_counter}) + "\n"
        try:
            conn.sendall(id_msg.encode())
        except Exception as e:
            print("Error sending client ID:", e)
            conn.close()
            continue

        # Find a valid spawn position.
        # Find a valid spawn position.
        while True:
            x = random.randint(0, len(game.game_map[0]) - 1)
            y = random.randint(0, len(game.game_map) - 1)
            if is_valid_spawn(game.game_map, x, y):
                if client_id_counter == 2 and not tagger_assigned:  # Second client is tagger
                    client_player = Player(float(x), float(y), role="tagger")
                    tagger_assigned = True
                else:
                    client_player = Player(float(x), float(y), role="runner")
                break


        with clients_lock:
            clients.append((client_id_counter, client_player, conn))
        threading.Thread(target=handle_client, args=(conn, client_id_counter, client_player), daemon=True).start()
        client_id_counter += 1

def main():
    port = int(input("Enter port: "))
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))
    server_socket.listen(5)  # Increase backlog if needed.
    print(f"Server listening on port {port}")

    game = Game()
    used_spawns = set()

    # Start accepting clients in a separate thread.
    threading.Thread(target=accept_clients, args=(server_socket, game, used_spawns), daemon=True).start()

    server_player = game.local_player

    # Main game loop: process input, update the game, render and broadcast state.
    running = True
    while running:
        running = game.display_map()  # This handles movement, rendering, and events.
        server_player.x = game.local_player.x
        server_player.y = game.local_player.y
        server_player.role = game.local_player.role
        broadcast_state(game, server_player)
        check_tagging(game)
    
    pygame.quit()  # Cleanly exit pygame when done.

if __name__ == "__main__":
    main()
