from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Country, Base, Missile, User

engine = create_engine('sqlite:///lots_of_missiles.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# create a dummy user
user1 = User(name="Akshay Menon", email="makshay@somewhere.com",
             picture='http://lorempixel.com/200/200/people/1')
session.add(user1)
session.commit()

user2 = User(name="Sharath Kumar", email="sharath@kumar.com",
             picture='http://lorempixel.com/200/200/people/2')
session.add(user2)
session.commit()

user3 = User(name="Mithun Airani", email="mithun@home.com",
             picture='http://lorempixel.com/200/200/people/3')
session.add(user3)
session.commit()

# Creating country and its missiles
firstCountry = Country(name="India", user_id=1)

session.add(firstCountry)
session.commit()

missile1 = Missile(name="Akash",
                   description="Surface to air missile.",
                   country=firstCountry,
                   link="https://en.wikipedia.org/wiki/Akash_(missile)",
                   user_id=1)
session.add(missile1)
session.commit()

missile2 = Missile(name="Nag",
                   description="Anti tank missile.",
                   country=firstCountry,
                   link="https://en.wikipedia.org/wiki/Nag_(missile)",
                   user_id=2)
session.add(missile2)
session.commit()

missile3 = Missile(name="Amogha Missile",
                   description="Anti tank missile.(under development)",
                   link="https://en.wikipedia.org/wiki/Amogha_missile",
                   country=firstCountry,
                   user_id=1)
session.add(missile3)
session.commit()

missile4 = Missile(name="Prithvi-I",
                   description="surface to surface Ballistic Missile",
                   link="https://en.wikipedia.org/wiki/Prithvi_(missile)#Prithvi_I",
                   country=firstCountry,
                   user_id=3)
session.add(missile4)
session.commit()

missile5 = Missile(name="Prithvi-II",
                   description="surface to surface Ballistic Missile",
                   link="https://en.wikipedia.org/wiki/Prithvi_(missile)#Prithvi_II",
                   country=firstCountry,
                   user_id=1)
session.add(missile5)
session.commit()

missile6 = Missile(name="Prithvi-III",
                   description="surface to surface Ballistic Missile",
                   link="https://en.wikipedia.org/wiki/Prithvi_(missile)#Prithvi_III",
                   country=firstCountry,
                   user_id=2)
session.add(missile6)
session.commit()


# Second Country and its missiles
secondCountry = Country(name="United Kingdom", user_id=1)

session.add(secondCountry)
session.commit()

missile1 = Missile(name="Bloodhound",
                   description="Surface to air missile.",
                   country=secondCountry,
                   link="https://en.wikipedia.org/wiki/Bristol_Bloodhound",
                   user_id=3)
session.add(missile1)
session.commit()

missile2 = Missile(name="Blowpipe",
                   description="Man portable Surface-to-air",
                   country=secondCountry,
                   link="https://en.wikipedia.org/wiki/Blowpipe_missile",
                   user_id=1)
session.add(missile2)
session.commit()

missile3 = Missile(name="Blue Steel",
                   description="Nuclear Stand Off Bomb",
                   link="https://en.wikipedia.org/wiki/Blue_Steel_missile",
                   country=secondCountry,
                   user_id=2)
session.add(missile3)
session.commit()

missile4 = Missile(name="Fairy Stooge",
                   description="anti-ship missile",
                   link="https://en.wikipedia.org/wiki/Fairey_Stooge",
                   country=secondCountry,
                   user_id=1)
session.add(missile4)
session.commit()


# Third Country and its missiles.
thirdCountry = Country(name="Russia", user_id=1)

session.add(thirdCountry)
session.commit()

missile5 = Missile(name="RT-21 Temp 2S",
                   description="mobile intercontinental ballistic missile (SS-16 Sinner)",
                   link="https://en.wikipedia.org/wiki/RT-21_Temp_2S",
                   country=thirdCountry,
                   user_id=3)
session.add(missile5)
session.commit()

missile6 = Missile(name="RT-21M Pioner",
                   description="mobile medium range ballistic missile (SS-20 Saber)",
                   link="https://en.wikipedia.org/wiki/RT-21M_Pioner",
                   country=thirdCountry,
                   user_id=3)
session.add(missile6)
session.commit()

missile5 = Missile(name="S-300P missille",
                   description="(SA-10 Grumble/SA-N-6/SA-20 Gargoyle/SA-X-21 Triumf)",
                   link="https://en.wikipedia.org/wiki/SA-10_Grumble",
                   country=thirdCountry,
                   user_id=1)
session.add(missile5)
session.commit()

missile6 = Missile(name="UR-100N",
                   description=" intercontinental ballistic missile (SS-19 Stiletto)",
                   link="https://en.wikipedia.org/wiki/UR-100N",
                   country=thirdCountry,
                   user_id=1)
session.add(missile6)
session.commit()
session.commit()
