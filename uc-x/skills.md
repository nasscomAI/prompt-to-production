skills:

- name: route_request
  description: Determines which agent should process the user request.
  inputs: user_request (string)
  outputs: agent_name (string)
  error_handling: If request type cannot be determined, return "unknown".

- name: coordinate_agents
  description: Coordinates the interaction between multiple agents to produce the final response.
  inputs: user_request (string)
  outputs: final_response (string)
  error_handling: If processing fails, return "Request could not be processed".