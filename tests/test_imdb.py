import pytest
import requests
from bs4 import BeautifulSoup

from websites import IMDB, IMDBReview


@pytest.fixture
def imdb():
    return IMDB()


@pytest.fixture
def review_block():
    review_html = """
<div class="lister-item mode-detail imdb-user-review with-spoiler" data-initialized="true" data-review-id="rw8168012" data-vote-url="/title/tt1745960/review/rw8168012/vote/interesting">
<div class="review-container">
<div class="lister-item-content">
<div class="ipl-ratings-bar">
<span class="rating-other-user-rating">
<svg class="ipl-icon ipl-star-icon" fill="#000000" height="24" viewbox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
<path d="M0 0h24v24H0z" fill="none"></path>
<path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"></path>
<path d="M0 0h24v24H0z" fill="none"></path>
</svg>
<span>10</span><span class="point-scale">/10</span>
</span>
</div>
<a class="title" href="/review/rw8168012/?ref_=tt_urv"> The truly epic blockbuster we needed.
</a> <div class="display-name-date">
<span class="display-name-link"><a href="/user/ur64798417/?ref_=tt_urv">Top_Dawg_Critic</a></span><span class="review-date">23 May 2022</span>
</div>
<span class="spoiler-warning">Warning: Spoilers</span>
<div class="actions text-muted">
                    2,647 out of 2,984 found this helpful.
                        <span>
                            Was this review helpful? <a href="/registration/signin?ref_=urv"> Sign in</a> to vote.
                        </span>
<br/>
<a href="/review/rw8168012/?ref_=tt_urv">Permalink</a>
</div><div class="ipl-expander">
<div class="ipl-expander__container">
<div class="expander-icon-wrapper spoiler-warning__control">
<svg class="ipl-expander__icon expander-icon" height="8" viewbox="0 0 12 8" width="12" xmlns="http://www.w3.org/2000/svg">
<path d="M10.197 0L6 4.304 1.803 0 0 1.85 6 8l6-6.15" fill="#2572B3" fill-rule="evenodd"></path>
</svg>
</div>
</div>
</div>
<div class="content">
<div class="text show-more__control">Wow. The first Top Gun is a classic, and as we all know, sequels/remakes rarely beat the original, especially 36 years later e.g. The Matrix Resurrections. Well, this film just broke that theory.<br/><br/>Aside from the adrenaline-pumping edge or your seat action, this story also had heart. It successfully overachieves, and surpasses its predecessor on every level.<br/><br/>The directing by novice Joseph Kosinski was outstanding, especially considering this was his fourth ever full length feature film. All the stunts, visuals and V/SFX were breathtaking, and the camera work perfection, that you'll feel you're in the cockpit of the jet. The soundtrack and score was amazing. The 131 min runtime literally flew by with its spot-on pacing. I actually wanted to see more. Casting and performances by all were also perfection, and once again Tom Cruise reminds us why he is still one of the top actors in the industry.<br/><br/>There's nothing I can critique or wish was better, as this gem was perfect in every way. Absolutely stunning, action-packed with a compelling and emotional story, as well as being a visual masterpiece. And the fact the dog fights were real and not CGI (actors had to train to fly the jets), just makes this film that much more magnificent. I'll be definitely seeing this again and adding the DVD to my collection. It's a rare perfect 10/10 must see from me.</div>
</div>
</div>
<div class="clear"></div>
</div>
</div>
    """
    return BeautifulSoup(review_html, "html.parser")


def test_parse_date(imdb, review_block):
    result = imdb.parse_date(review_block)
    assert isinstance(result, str)


def test_parse_rating(imdb, review_block):
    rating, rating_ratio = imdb.parse_rating(review_block)
    assert isinstance(rating, str)
    assert isinstance(rating_ratio, float)


def test_parse_review(imdb, review_block):
    result = imdb.parse_review(review_block)
    assert isinstance(result, str)


def test_parse_upvotes(imdb, review_block):
    upvotes, total_votes = imdb.parse_upvotes(review_block)
    assert isinstance(upvotes, int)
    assert isinstance(total_votes, int)


def test_parse_permalink(imdb, review_block):
    result = imdb.parse_permalink(review_block)
    assert isinstance(result, str)


def test_parse_review_block(imdb, review_block):
    result = imdb.parse_review_block(review_block)
    assert isinstance(result, IMDBReview)


def test_parse_reviews(imdb, review_block):
    review_blocks = [review_block, review_block]
    result = imdb.parse_reviews(review_blocks)
    assert isinstance(result, list)
    assert all(isinstance(r, IMDBReview) for r in result)
