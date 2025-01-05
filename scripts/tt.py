from friday.connectors.jira_client import JiraConnector

yo = JiraConnector().get_issue_details("FRID-1")
print(yo.get("summary"))
