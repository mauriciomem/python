After watching Arjan's video on "Requests vs. HTTPX vs. Aiohttp | Which One to Pick?", added to the fact that currently in my work I need to develop small tools or scripts to automate tasks and extract data in Kubernetes clusters, I decided to compare HTTP libraries and Kubernetes clients in Python, to identify which one has the shortest response times.
The objective of this analysis is to measure the performance of each library and/or client in terms of response times in handling network IO operations. From the initiation of the HTTP request, through a method provided by the tested library, to the reception of the required data or library/client object. Aspects such as data structure manipulation in the response and concurrency load supported by each library/client, among other features, are not covered in what is explained below.
Core questions:
Is it worth replacing Kubernetes clients with HTTP libraries when response time is a priority?
Are we willing to assume the complexity required by coding with a lower level of abstraction because of performance improvements?

Besides the analysis results exposed below, these questions will depend on your context, time, and project scope.
Why Python?
Although Go is the de facto standard for Kubernetes and its ecosystem, Python is a viable alternative due to its widespread usage, fast learning curve, and versatility in creating tools rapidly. Additionally, the design, structure, and HTTP interface of the Kubernetes API allows you to quickly start exploring and manipulating its resources via HTTP methods.
By simply running kubectl get --raw /, we can retrieve the list of available resource URIs in a cluster, and coupled with the use of standard HTTP methods to operate on the resources, the manipulation of the cluster resources is a well-known task. It's possible to use curl or any client library from Go, Python, Ruby, etc.
For these reasons, I gathered some of the best-known available HTTP clients and Kubernetes clients in Python. Looking at the available HTTP clients, I selected the Requests, HTTPX, and aiohttp libraries. Also, for the Python Kubernetes clients, I chose the official client, lightkube, pykube-ng, and kr8s.
I added asynchronous tests with the help of the asyncio library for a few reasons: its increasingly widespread usage, its growing implementation in various Kubernetes clients, and out of curiosity to verify if, for these IO time-focused tests, concurrency usage produces substantial changes. 
Furthermore, I wanted to check if leveraging asyncio features contributes to improving response times. Indeed, using methods that execute tasks concurrently reduces response time, especially for any requests that can be initiated simultaneously. These features come with a cost, as implementing concurrency also requires extra care and attention that we might not take into account with synchronous code.
By considering a library or client's network IO response time as the only factor to measure performance, we would only measure its efficiency in managing a network stack in establishing, transmitting, and terminating an HTTP request. However, the main focus of this analysis is how we can take advantage of Python features to squeeze the best response times out of the libraries and clients analyzed.
Platforms
From an infrastructure perspective, three types of clusters were used, all in version 1.28, with similar computing capabilities but with different deployments. The first is a locally deployed Minikube cluster, the second is an EKS-managed cluster deployed on AWS, and the third is an upstream Kubernetes solution (vanilla Kubernetes) deployed on EC2 instances in AWS.
Minikube
Specs: 1 control plane node, 3 worker nodes, CNI Calico, Podman driver. Default hardware resources (2 CPU cores, 2048 GB RAM per container)
Template: minikube start -p k8s -n 4 --network-plugin=cni --cni=calico --kubernetes-version=1.28.0 --driver=podman
Upstream/Vanilla Kubernetes
Specs: 2 t3.small control plane nodes, 2 t3.micro worker nodes, and one t3.small HA proxy acting as a load balancer. Deployed in the us-east-1 region
Template: kube-the-hard-way-aws
EKS
Specs: AWS Managed control plane, 1 node group with t3.micro instances, deployed in the us-east-1 region
Template: eksctl demo cluster
Response time metric
Regarding the code details of each library/client, I simply use the built-in time module to encapsulate each response time measurement in two essential steps:
Initialization of the HTTP library class method or the Kubernetes client object.
Read and write requests, from invocation to response, in the format handled by each library or client.

Each test scenario consisted of 50 iterations of each library and client to every endpoint at three different moments during the day (morning, afternoon, and night), totaling 450 iterations per library and client.
The read and write requests involved: 4 read requests (namespaced and non-namespaced resources) and 2 write requests, specifically creating and deleting a namespace.
Why are read and write requests included in one iteration?
To check if a session object of a library can optimize the network handling of an HTTP connection with many requests involved. For example, requests.get() vs requests.Session() 
How concurrency can improve overall performance.

This repo has the code of every library or client used as a test scenario, the generated graphs, and the dataset.
HTTP libraries
Except for the Request library, most HTTP libraries outperformed the response time of the Kubernetes clients. As a downside, coding the libraries to work with the Kubernetes API endpoint required at least:
Managing the authentication workflow from the Kubernetes API perspective, with subtle differences between each endpoint. On one hand, Minikube and Upstream/Vanilla Kubernetes use client certificates to provide authentication. EKS, on the other hand, uses ExecCredentials as a means of generating and sending a bearer token to the API endpoint.
Creating the logic required for securing the connection to the Kubernetes API depends on each library session object and its security parameters. For example, aiohttp uses an SSLContext object included in the SSL built-in library to load the client certificates, but in HTTPX you can load them directly in its session object.
Create the logic required to transverse the resource URIs present in the API endpoint depending on the Kubernetes resource needed.

In each test scenario listed below, I created the necessary logic to handle these main requirements.
Requests
With the Requests library, I wanted to confirm what Arjan mentioned in his video, considering Kubernetes endpoints specifically. Each Requests scenario differs in whether its requests.Session() object is invoked or not.
Test scenarios
req_sync_nosess - Requests sync HTTP client, no session object.
req_sync_sess - Requests sync HTTP client with the session object.

Reference: Request, Requests session objects
Aiohttp
I avoided installing the aiodns library to ensure that the rest of the clients were under the same testing conditions. However, measuring the potential difference in response times that aiodns may represent is still pending.
aiohttp_async executes all tasks on read operations concurrently with asyncio.gather() and then executes write tasks sequentially, all within a context manager calling the aiohttp.ClientSession()object.
aiohttp_async_c includes a wrapper async function to run all reading and writing tasks concurrently, with extra care to ensure the writing tasks are run one after another. Again, this process is run inside the context manager of theaiohttp.ClientSession()object.
Test scenarios:
aiohttp_async_c - aiohttp asynchronous HTTP client with "concurrent" executions.
aiohttp_async - aiohttp asynchronous HTTP client with "sequential" executions.

Reference: aiohttp
HTTPX
HTTPX is a great library that aims to fusion the elegance and simplicity of Requests and the performance of aiohttp, including the support of async and sync methods. Regarding HTTPX, I only tested its async API, replicating an approach identical to the aiohttp test scenarios.
Test scenarios:
httpx_async_c - HTTPX async HTTP client with "concurrent" executions.
httpx_async - HTTPX async HTTP client with "sequential" executions.

Reference: httpx
Kubernetes clients
Comparing all Kubernetes clients, the first evidence that stands out from the graphs is the clear difference in response time between the vanilla/upstream Kubernetes and EKS. Could these results arise as a consequence of how EKS scales its control plane depending on its load, concurrency, and overall cluster usage? Does it affect the authentication workflow to the EKS endpoint? Or does the abstraction layer by each client logic add a special overhead to this endpoint? These questions weren't answered by this analysis.
Keep in mind that Kubernetes clients present a considerable difference in the ease of use and development speed with the Kubernetes API, involving just a few lines of code to have a running solution for your daily tasks in Kubernetes.
kr8s
Test scenarios:
kr8s_async - kr8s client library for Kubernetes, async API
kr8s_sync - kr8s client library for Kubernetes, sync API

Reference: kr8s, kr8s.asyncio
Oficial Kubernetes library
Test scenario:
k8s_sync - Oficial Kubernetes library, only supports a sync API

Reference: kubernetes-client
Unofficial Kubernetes async library
Test scenarios:
k8s_async - Async library based on the oficial Kubernetes library

Reference: kubernetes_asyncio
Lightkube
Test scenarios:
lightkube_async - Test lightkube kubernetes client with async API.
lightkube_sync - Test lightkube kubernetes client with sync API.

Reference: lightkube, lightkube async
Pykube-NG
Test scenarios:
pykube-ng_async - A lightweight Kubernetes client library tuned to support async/await features.
pykube-ng_sync - A lightweight Kubernetes client library, straightforward use in sync mode

Reference: pykube-ng
Results
The first graph shows the mean response times per client with respect to each endpoint. The idea of including Minikube is to identify whether clients show a correlation in response times across all tested endpoints.
Mean response time of each Python clientFor the tested HTTP libraries, HTTPX, Requests, and aiohttp maintained their trend of response times on each of the endpoints, where aiohttp_async_c emerged with the best mean results on each endpoint, and req_sync_nosess being the worst result on all endpoints.
Regarding Kubernetes clients, surprisingly, the lightkube_sync test dethroned its asynchronous alternative. In these tests, there was no clear winner between asynchronous and synchronous options, and, in fact, the performance of the former was worse, especially for local tests on Minikube, where network IO becomes less relevant. What is evident is that response times on the endpoint presenting the upstream version of Kubernetes were clearly lower than those of the EKS cluster. It will remain to identify the characteristics of the EKS control plane managed by AWS directly. According to the test conditions, it seems that the t3 instances that make up the control plane and the load balancer are sufficient to surpass the performance of the EKS cluster (in this scenario, concurrency load tests would be ideal to compare how performance is sustained over time).
Total iterations of each cloud endpoint broken down by timeFrom another perspective, to focus on the difference between the cloud endpoints and to help identify the dispersion of the results shown in the previous graph, the histogram helps us identify that the majority of requests to the vanilla/upstream endpoint resulted in reduced response times compared to the EKS endpoint.
If we compare all iterations across all evaluated clients and group them according to endpoints, performance remains constant as iterations progress. There are no significant dispersions between each client's evaluated response time.
Response time of each iteration per round (morning, afternoon, and night)It can be identified that at the beginning of each iteration round, there is a sharp increase in response times, probably required by the establishment of the network connection and all the steps this involves, from packet routing through the creation of the TCP connection, name resolution of the endpoints to the TLS negotiation and authentication process, and the transmission of the payload between the client and server ends. Later on, I review if there is any particular client or clients that cause the distortion at the start of the round.
Finally, at the beginning of the first round, in the morning, a small increase in response times is observed between iterations 20 and 40.
Response time of each iteration per HTTP library on every endpointResponse time of each iteration per HTTP library, on cloud endpoints onlyBreaking down the previous graph by HTTP libraries only, the difference in response times during all iterations between the EKS and vanilla endpoints is not clearly identifiable. Only the Requests library had special difficulties in maintaining response times similar to the upcoming rounds, especially the test that does not instantiate a session object, causing each HTTP method used by the library to involve a longer connection establishment process.
Response time of each iteration per Kubernetes client on every endpointResponse time of each iteration per Kubernetes client on cloud endpoints onlyAnalyzing Kubernetes clients, they generally present slightly higher response times, probably due to overhead produced by their abstraction and ease of use. In particular, according to the tests conducted, the kr8s client showed a much slower start on every round than the rest.
Best HTTP library and Kubernetes client performersFinally, in the comparison between the best performances of each group, aiohttp_async_c vs. lightkube_sync, the difference on the upstream/vanilla Kubernetes endpoint is rather negligible. Only the EKS endpoint performance suffered from a clear performance in the lightkube sync test.
Conclusions
The results could show us how the craftmanship of each library had an impact on response time performance. Libraries and clients, such as aiohttp, HTTPX, and lightkube, shined with great mean response times and were consistent during the iterations in every round.
Also, to focus the analysis on a response time metric of a network IO bound task and relax the emphasis on the concurrency load of each library/client, hide the potential of the asynchronous tests, matching their overall performance with the synchronous tests. However, we could grasp the performance benefits of implementing async by pushing the API request to be executed concurrently in the aiohttp and HTTPX tests.
The management of the network stack by the HTTP libraries, with the exception of Requests, is very similar in terms of response time performance. Again, we don't make enough use of the asynchronous potential of running tasks concurrently.
From the side of the Kubernetes clients, the worst performer was the k8s_sync library and its async fork, which nearly matches the performance of the Request library test with the session object.
If we try to answer the questions asked at the beginning of the article, it seems rather clear that there are available Kubernetes clients that can stand a fight against pure HTTP libraries.