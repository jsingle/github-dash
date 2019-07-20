import os

from github import Github, UnknownObjectException

class OrganizationNotFoundException(Exception):
	pass

github_client = None
RETURN_LIST_SIZE = 5

def _client():
	global github_client
	if github_client is not None:
		return github_client
	token = os.environ['GITHUB_TOKEN']
	github_client = Github(token)
	return github_client

def _organization(name):
	try:
		return _client().get_organization(name)
	except UnknownObjectException:
		raise OrganizationNotFoundException()

def _sort_repos_by_stars(repos):
	sorted_repos = sorted(repos, key=lambda repo: repo.stargazers_count, reverse=True)
	return list(map(lambda repo: (repo.name, repo.stargazers_count), sorted_repos))

def _sort_repos_by_forks(repos):
	sorted_repos = sorted(repos, key=lambda repo: repo.forks_count, reverse=True)
	return list(map(lambda repo: (repo.name, repo.forks_count), sorted_repos))

# Returns tuple of (repo_name, contributors_count) sorted by contributor count
def _sort_repos_by_contributors(repos, contributors):
	repos_names = map(lambda repo: repo.name, repos)
	contributors_counts = map(lambda contributors: len(contributors), contributors)
	return sorted(zip(repos_names, contributors_counts), key=lambda repo_and_contributors: repo_and_contributors[1], reverse=True)

# Returns tuple of (login, contributions_count) sorted by contributions_count
def _sort_contributors_by_contributions(repos_contributors):
	contributions_by_login = {} # dict of login to contribution count across all repos
	for repo_contributors in repos_contributors:
		for contributor in repo_contributors:
			login = contributor.author.login
			count_for_repo = contributor.total
			contributions_by_login[login] = contributions_by_login.get(login, 0) + count_for_repo
	return sorted(contributions_by_login.items(), key=lambda login_and_count: login_and_count[1], reverse=True)

def get_repos_summary(organization_name):
	organization = _organization(organization_name)
	repos = list(organization.get_repos())
	repos_by_stars = _sort_repos_by_stars(repos)
	repos_by_forks = _sort_repos_by_forks(repos)
	return {
		'repos_by_stars': repos_by_stars[0:RETURN_LIST_SIZE],
		'repos_by_forks': repos_by_forks[0:RETURN_LIST_SIZE],
	}

def get_top_contributors(organization_name):
	organization = _organization(organization_name)
	repos = list(organization.get_repos())
	members = organization.get_members()
	member_logins = set(map(lambda member: member.login, members))
	contributors = list(map(lambda repo: list(repo.get_stats_contributors() or []), repos))
	repos_by_contributors = _sort_repos_by_contributors(repos, contributors)
	all_contributors_sorted = _sort_contributors_by_contributions(contributors)
	internal_contributors_sorted = list(filter(lambda login_and_count: login_and_count[0] in member_logins, all_contributors_sorted))
	external_contributors_sorted = list(filter(lambda login_and_count: login_and_count[0] not in member_logins, all_contributors_sorted))
	return {
		'repos_by_contributors': repos_by_contributors[0:RETURN_LIST_SIZE],
		'top_internal_contributors': internal_contributors_sorted[0:RETURN_LIST_SIZE],
		'top_external_contributors': external_contributors_sorted[0:RETURN_LIST_SIZE],
	}
