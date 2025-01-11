import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.graph_objs as go

# Load dataset
data = {
    "Year": list(range(2000, 2010)),
    "Temperature_Anomaly": [0.25, 0.29, 0.33, 0.38, 0.41, 0.45, 0.50, 0.55, 0.60, 0.62],
}
df = pd.DataFrame(data)

# Initialize Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div(
    [
        html.H1("Data Trend Guessing Game", style={"textAlign": "center"}),

        # Graph displaying data up to the current year
        dcc.Graph(id="trend-graph"),

        # Buttons for player to guess
        html.Div(
            [
                html.Button("Increase", id="btn-increase", n_clicks=0, style={"margin-right": "10px"}),
                html.Button("Decrease", id="btn-decrease", n_clicks=0),
            ],
            style={"textAlign": "center", "margin-top": "20px"},
        ),

        # Display game status
        html.Div(id="game-status", style={"textAlign": "center", "margin-top": "20px"}),

        # Hidden div to store game state
        dcc.Store(id="game-state", data={"current_index": 0, "score": 0}),
    ]
)

# Callback to update graph based on game state
@app.callback(
    Output("trend-graph", "figure"),
    Input("game-state", "data")
)
def update_graph(game_state):
    current_index = game_state["current_index"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Year"][:current_index + 1],
        y=df["Temperature_Anomaly"][:current_index + 1],
        mode="lines+markers",
        line=dict(color="blue"),
    ))
    fig.update_layout(
        title="Global Temperature Anomalies",
        xaxis_title="Year",
        yaxis_title="Temperature Anomaly (°C)",
    )
    return fig

# Callback to handle user input and game state updates
@app.callback(
    Output("game-state", "data"),
    Output("game-status", "children"),
    Input("btn-increase", "n_clicks"),
    Input("btn-decrease", "n_clicks"),
    State("game-state", "data"),
)
def handle_guess(btn_increase, btn_decrease, game_state):
    current_index = game_state["current_index"]
    score = game_state["score"]

    # Check which button was clicked
    ctx = dash.callback_context
    if not ctx.triggered:
        return game_state, ""

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    next_value = df["Temperature_Anomaly"][current_index + 1]
    current_value = df["Temperature_Anomaly"][current_index]

    if button_id == "btn-increase":
        user_guess = "Increase"
        correct = next_value > current_value
    elif button_id == "btn-decrease":
        user_guess = "Decrease"
        correct = next_value < current_value
    else:
        return game_state, ""

    # Update game state
    if correct:
        score += 1
        feedback = f"Correct! Your score is now {score}."
    else:
        feedback = f"Wrong! The correct trend was {'Increase' if next_value > current_value else 'Decrease'}."

    current_index += 1

    # Check if game has ended
    if current_index >= len(df) - 1:
        feedback += " You've reached the end of the game!"
        current_index = len(df) - 1  # Keep index from going out of bounds

    game_state["current_index"] = current_index
    game_state["score"] = score

    return game_state, feedback

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)