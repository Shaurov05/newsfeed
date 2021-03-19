# newsfeed
User can see news from NewsTeller through API. User can configure search list and get filtered news from NewsTeller.
A background task collects news using the API and stores only the lastest news in the database so that the user can see the updated news.

<h2> Setting up the environment </h2>

<li> Create a virtual environment using python</li>
<li> After creating an envionment run these commands on terminal: </li>
<ol>
  <li>  pip install -r requirements.txt</li>
  <li> python manage.py makemigations</li>
  <li> python manage.py migrate</li>
  <li> python manage.py runserver </li>
  <li> python manage.py process_tasks </li>
 </ol>
 
<h3> API endpoints </h3> 
<ol>
  <li>'newsfeed': 'http://127.0.0.1:8000/user/api/newsfeed/'</li>
  <li>"userProfile": "http://127.0.0.1:8000/user/api/userProfile/"</li>
  <li>"user": "http://127.0.0.1:8000/user/api/user/"</li>
  <li>"login": "http://127.0.0.1:8000/api/auth/login/"</li>
</ol>
  
 <h3>News Feed </h3>
<ol>
  <li>User can see the list of NewsFeeds</li>
  <li>User can see the details of a single News! </li>
</ol>

<h3>User Profiles </h3>
<ol>
  <li>User can see the list of User Profiles where country, sources and keywords choices are listed! </li>
  <li>User can see the details of a user profile! </li>
</ol>

<h3> User</h3>
<ol>
  <li>User can see the list of users</li>
  <li>User can register sending username, password, email thorugh POST request</li>
</ol>

<h3>Login</h3>
<ol>
  <li>User can send username and password through a POST request and recieve a token using which user can see details of User Profiles and personalized news feed.</li>
</ol>
