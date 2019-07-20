import logging

from flask import Flask, abort, request, render_template

from src.github import get_repos_summary, get_top_contributors, OrganizationNotFoundException

app = Flask(__name__)

def _render_organization_dash(name, summary):
	return render_template('organization_dash.html', organization_name=name, summary_stats=summary)

def _render_top_contributors(name, summary):
	return render_template('organization_top_contributors.html', organization_name=name, summary_stats=summary)

def _render_organization_not_found(name):
	return render_template('organization_not_found.html', organization_name=name)

@app.route('/', methods=['GET'])
def route_index():
    return render_template('index.html')

@app.route('/organization-dash', methods=['GET'])
def route_organization_dash():
	organization_name = request.args.get('name', default=None)
	try:
		summary = get_repos_summary(organization_name)
		print(summary)
		return _render_organization_dash(organization_name, summary)
	except OrganizationNotFoundException:
		return _render_organization_not_found(organization_name)

# This is split out into a separate endpoint because it takes much longer to query the github API for the
# underlying data.  This way the other endpoint can still cheaply return the data that is cheap to query
@app.route('/organization-top-contributors', methods=['GET'])
def route_organization_top_contributors():
	organization_name = request.args.get('name', default=None)
	try:
		summary = get_top_contributors(organization_name)
		print(summary)
		return _render_top_contributors(organization_name, summary)
	except OrganizationNotFoundException:
		return _render_organization_not_found(organization_name)
