import uuid

from flask import blueprints, request, render_template, jsonify, session

from Model.classes import Game, Player


def get_blueprint(path: str = '') -> blueprints.Blueprint:
    index_bp = blueprints.Blueprint('index', __name__)

    @index_bp.route('/')
    def index():
        # 生成游戏ID，可以使用随机生成的唯一标识符
        if 'game_id' not in session:
            session['game_id'] = f'Game_{str(uuid.uuid4().hex[:6])}'
        else:
            try:
                Game.del_game(session['game_id'])
            except ValueError:
                pass
        Game(session['game_id'])

        return render_template('index.html', route=path)

    @index_bp.route('/api/new_round', methods=['POST'])
    def new_round():
        # 获取发送的 JSON 数据
        data = request.get_json()
        king = data['king']
        score = data['score']

        # 这里执行你的新回合逻辑，调用相应的方法处理玩家和分数
        try:
            Game.get_game_by_id(session['game_id']).new_round(king, score)
        except ValueError:
            response_data = {'message': 'Invalid input'}
            return jsonify(response_data)
        # 返回一个 JSON 响应，表示新回合已经处理完成
        response_data = {'message': 'New round started successfully'}
        return jsonify(response_data)

    @index_bp.route('/api/history')
    def get_history():
        return jsonify(Game.get_game_by_id(session['game_id']).history_json)

    @index_bp.route('/api/restart', methods=['POST'])
    def restart():
        Game.get_game_by_id(session['game_id']).restart()
        return jsonify({'message': 'Game restarted successfully'})

    @index_bp.route('/api/set_player_names', methods=['POST'])
    def set_player_name():
        def instantiate_player(name: str) -> Player:
            try:
                result = Player(name, session['game_id'])
            except ValueError:
                result = Player.get_player_by_name(name, session['game_id'])
            return result

        data = request.get_json()
        player_name = data['playerNames']
        player = list(map(instantiate_player, player_name))
        Game.get_game_by_id(session['game_id']).players = player
        return jsonify({'message': 'Player name set successfully'})

    @index_bp.route('/api/get_players')
    def get_player_name():
        return jsonify(Game.get_game_by_id(session['game_id']).players)

    @index_bp.route('/api/new_game', methods=['POST'])
    def new_game_route():
        Game.del_game(session['game_id'])
        Game(session['game_id'])
        # 返回 JSON 响应
        return jsonify({'message': 'New game created successfully'}), 200

    @index_bp.route('/api/clear_player_score', methods=['POST'])
    def clear_player_score():
        Player.clear_all_score(session['game_id'])
        return jsonify({'message': 'Player score cleared successfully'})

    @index_bp.route('/api/cancel_round', methods=['POST'])
    def cancel_round():
        try:
            Game.get_game_by_id(session['game_id']).cancel_round()
        except OverflowError:
            return jsonify({'message': 'Round canceled failed'}), 400
        return jsonify({'message': 'Round canceled successfully'})

    @index_bp.route('/api/close')
    def close():
        Game.del_game(session['game_id'])

    return index_bp
