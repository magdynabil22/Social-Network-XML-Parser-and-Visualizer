from Tree import Tree
from Graph import DirectedGraph
import networkx as nx
import matplotlib.pyplot as plt


class Network:
    # 1. Most Influential Users (Most Followers)
    def most_influential(graph):
        user_ids = []
        out_degrees = []

        for user in graph.nodes:
            user_ids.append(user.id)
            out_degrees.append(len(graph.successors(user.id)))

        max_out_degree = max(out_degrees)

        most_influential_users = [
            user_ids[i]
            for i, degree in enumerate(out_degrees)
            if degree == max_out_degree
        ]

        print(f"The most influential users are: {most_influential_users}")
        return most_influential_users

    # 2. Most Active User (Connected to Lots of Users)
    def most_active(graph):
        user_ids = []
        total_edges = []

        for user in graph.nodes:
            user_ids.append(user.id)
            total_edges.append(graph.degree(user.id))

        max_total_edges = max(total_edges)

        most_active_users = [
            user_ids[i]
            for i, degree in enumerate(total_edges)
            if degree == max_total_edges
        ]

        print(f"The most active users are: {most_active_users}")
        return most_active_users

    # 3.  Mutual followers between 2 users
    def mutual_followers(graph, node1_id, node2_id):
        node1 = graph.find_node(str(node1_id))
        node2 = graph.find_node(str(node2_id))

        if not node1 or not node2:
            print("Invalid nodes. Please provide existing nodes.")
            return None

        followers_node1 = [
            successor.id for successor in graph.successors(str(node1_id))
        ]
        followers_node2 = [
            successor.id for successor in graph.successors(str(node2_id))
        ]

        mut_followers = [
            follower for follower in followers_node1 if follower in followers_node2
        ]
        print(
            f"Mutual followers between nodes {node1_id} and {node2_id}: {mut_followers}"
        )
        return mut_followers

    # 4.  Suggest users to follow
    def suggest_followers(graph):
        suggested_followers = []

        for user in graph.nodes:
            user_suggestions = []

            for successor in graph.successors(user.id):
                for suggested_follower in graph.successors(successor.id):
                    if (
                        suggested_follower not in graph.predecessors(user.id)
                        and suggested_follower.id != user.id
                        and suggested_follower.id not in user_suggestions
                    ):
                        user_suggestions.append(suggested_follower.id)

            suggested_followers.append((user.id, user_suggestions))

        for user, user_suggestions in suggested_followers:
            print(f"Suggested followers for User {user}: {user_suggestions}")

        return suggested_followers

    def create_graph(xml_file):
        tree = Tree()
        tree = tree.Parse(xml_file)
        root = tree.getroot()

        if root is not None:
            graph = DirectedGraph()

            for user in root.findall("user"):
                user_id = user.find("id").value

                if user.find("name") is not None:
                    user_name = user.find("name").value
                else:
                    user_name = "unknown"
                graph.add_node(user_id, name=user_name)

                followers = user.find("followers")
                if followers is not None:
                    for follower in followers.findall("follower"):
                        follower_id = follower.find("id").value
                        graph.add_edge(user_id, follower_id)

                user_posts = user.find("posts")
                if user_posts is not None:
                    posts = []
                    for post in user_posts.findall("post"):
                        posts.append(post)

                    graph.add_posts(user_id, posts)

            # Create a directed graph from your data using NetworkX
            nx_graph = nx.DiGraph()

            for node in graph.nodes:
                nx_graph.add_node(node.id, name=node.name)
                for successor in node.successors:
                    nx_graph.add_edge(node.id, successor.id)

            # Visualize the graph
            pos = nx.spring_layout(nx_graph)  # You can use different layout algorithms
            nx.draw(
                nx_graph,
                pos,
                with_labels=True,
                font_weight="bold",
                node_size=700,
                node_color="skyblue",
                arrowsize=10,
                font_size=8,
                edge_color="skyblue",
                connectionstyle="arc3,rad=0.1",
            )
            plt.show()

            return graph
        else:
            print("Error: Tree root is not properly set.")
            return None

    def post_search(graph, keyword):
        matching_posts = []

        for user in graph.nodes:
            user_name = user.name
            user_posts = user.posts

            for post in user_posts:
                if post.find("body") is not None:
                    post_body = post.find("body").value
                else:
                    post_body = ""

                # Check if the keyword is present in the post body
                if keyword.lower() in post_body.lower():
                    matching_posts.append((user.id, user_name, post_body))
                    continue

                # Check if the keyword is present in any topic
                topics = post.find("topics")
                if topics is not None:
                    for topic in topics.findall("topic"):
                        topic_text = topic.value
                        if keyword.lower() in topic_text.lower():
                            matching_posts.append((user.id, user_name, post_body))
                            break

        if not matching_posts:
            print(
                f"There is no post whose topic is '{keyword}' or contain the keyword '{keyword}'."
            )
        else:
            print(
                f"Posts whose topic is '{keyword}' or contain the word '{keyword}' in it:"
            )
            for user_id, user_name, post_body in matching_posts:
                print(f"User ID: {user_id}, Name: {user_name}, Post: {post_body}\n")

        return matching_posts
