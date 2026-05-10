import json
from datetime import datetime, timezone, timedelta
from flask import Blueprint, render_template, request, jsonify, session

from ..tools.comexstat_tool import ComexStatClient
from ..models import ComexstatCache, SessionLocal

bp = Blueprint('comexstat', __name__, url_prefix='/comexstat')

COUNTRIES_CACHE = []
STATES_CACHE = []
CACHE_LOADED = False


def _get_db():
    if SessionLocal is None:
        from ..models import init_db
        globals()['SessionLocal'] = init_db()[1]
    return SessionLocal()


def _user_id():
    return str(session.get('user_id', 'default'))


def _load_cache():
    global COUNTRIES_CACHE, STATES_CACHE, CACHE_LOADED
    if CACHE_LOADED:
        return
    try:
        client = ComexStatClient(timeout=10)
        data_countries = client.get_countries()
        data_states = client.get_states()
        COUNTRIES_CACHE = data_countries if isinstance(data_countries, list) else []
        STATES_CACHE = data_states if isinstance(data_states, list) else []
        CACHE_LOADED = True
    except Exception:
        COUNTRIES_CACHE = []
        STATES_CACHE = []


@bp.route('/')
def dashboard():
    client = ComexStatClient(timeout=10)
    try:
        _load_cache()
        last_update = client.get_last_update()
        years = client.get_years()
    except Exception:
        last_update = ''
        years = {}

    return render_template('comexstat/dashboard.html',
                           last_update=last_update,
                           years=years,
                           countries=COUNTRIES_CACHE if isinstance(COUNTRIES_CACHE, list) else [],
                           states=STATES_CACHE if isinstance(STATES_CACHE, list) else [],
                           current_page='comexstat')


@bp.route('/history')
def history():
    uid = _user_id()
    db = _get_db()
    try:
        queries = db.query(ComexstatCache).filter_by(user_id=uid).order_by(
            ComexstatCache.consultado_em.desc()).limit(50).all()
        return render_template('comexstat/history.html',
                               queries=queries,
                               current_page='comexstat')
    finally:
        db.close()


def _save_cache(user_id, flow, ano, mes, pais, estado, ncm, modal, result_data):
    db = _get_db()
    try:
        entry = ComexstatCache(
            user_id=user_id,
            flow=flow,
            ano=ano,
            ncm=ncm,
            pais=pais,
            estado=estado,
            modal=modal,
            result_data=json.dumps(result_data[:200] if isinstance(result_data, list) else result_data, ensure_ascii=False),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        db.add(entry)
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


@bp.route('/api/query', methods=['POST'])
def api_query():
    data = request.get_json()
    client = ComexStatClient(timeout=30)
    try:
        ncm_raw = data.get('ncm')
        if ncm_raw:
            ncm_raw = ''.join(c for c in str(ncm_raw) if c.isdigit())
        if not ncm_raw:
            ncm_raw = None

        modal_val = data.get('modal')
        if modal_val:
            modal_val = str(modal_val).strip()

        result = client._query(
            flow=data.get('flow', 'export'),
            ano=data.get('ano', 2025),
            mes=data.get('mes'),
            pais=data.get('pais'),
            estado=data.get('estado'),
            ncm=ncm_raw,
            modal=modal_val,
        )

        # Save to cache
        _save_cache(
            user_id=_user_id(),
            flow=data.get('flow', 'export'),
            ano=data.get('ano', 2025),
            mes=data.get('mes'),
            pais=data.get('pais'),
            estado=data.get('estado'),
            ncm=ncm_raw,
            modal=modal_val,
            result_data=result,
        )

        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@bp.route('/api/top-products', methods=['POST'])
def api_top_products():
    data = request.get_json()
    flow = data.get('flow', 'export')
    ano = data.get('ano', 2025)
    limite = data.get('limite', 10)

    client = ComexStatClient(timeout=30)
    try:
        result = client._query(flow, ano)
        result.sort(key=lambda x: float(x.get('metricFOB', 0)), reverse=True)
        return jsonify({'success': True, 'data': result[:limite]})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@bp.route('/api/status')
def api_status():
    client = ComexStatClient(timeout=10)
    try:
        update = client.get_last_update()
        years = client.get_years()
        return jsonify({
            'connected': True,
            'last_update': update,
            'years': years,
        })
    except Exception:
        return jsonify({'connected': False, 'last_update': ''})
