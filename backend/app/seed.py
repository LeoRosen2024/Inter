from datetime import timedelta

from sqlmodel import Session, func, select

from app.core.config import get_settings
from app.db import engine
from app.models import AppSetting, Reel, ReelScript, SocialProfile, utcnow


COMPETITORS = [
    ("creatorlab", "Creator Lab", 284000, 4800000, 8.7), ("socialtipps", "Social Tipps", 196000, 3100000, 7.9),
    ("reelstudio", "Reel Studio", 142000, 2400000, 9.2), ("marketingde", "Marketing DE", 98000, 1700000, 6.8),
    ("growdaily", "Grow Daily", 76000, 1200000, 8.1), ("contentcoach", "Content Coach", 64000, 980000, 7.4),
    ("hookmaster", "Hook Master", 58000, 902000, 8.4), ("editacademy", "Edit Academy", 53000, 844000, 7.8),
    ("captionwerk", "Caption Werk", 49000, 791000, 8.0), ("socialplan", "Social Plan", 46000, 738000, 7.6),
    ("videosetup", "Video Setup", 43000, 694000, 7.2), ("storywerk", "Story Werk", 39000, 641000, 8.9),
    ("trendscout", "Trend Scout", 36000, 598000, 9.1), ("creatormind", "Creator Mind", 34000, 552000, 7.7),
    ("reelslab", "Reels Lab", 31000, 514000, 8.3), ("digitalalltag", "Digital Alltag", 29000, 477000, 7.5),
    ("marketingflow", "Marketing Flow", 27000, 438000, 8.2), ("videopraxis", "Video Praxis", 24000, 392000, 7.1),
    ("ideengarage", "Ideen Garage", 22000, 351000, 8.6), ("mediapro", "Media Pro", 19000, 306000, 7.3),
]

TREND_REELS = [
    ("Hook in 3 Sekunden", "creatorlab", 24, 42800, 98),
    ("Storytelling-Formel", "socialtipps", 31, 37200, 91),
    ("Content ohne Stress", "reelstudio", 18, 29400, 86),
    ("Die perfekte Caption", "marketingde", 27, 24900, 79),
    ("Mehr Reichweite", "growdaily", 22, 18700, 72),
    ("5 Fehler bei Reels", "contentcoach", 34, 17300, 70),
    ("Der perfekte Einstieg", "hookmaster", 19, 16800, 68),
    ("Algorithmus einfach erklärt", "digitalalltag", 42, 15100, 65),
    ("Mehr Kommentare erhalten", "creatormind", 25, 13900, 63),
    ("Reels richtig planen", "socialplan", 29, 12600, 61),
    ("Licht für dein Video", "videopraxis", 21, 11800, 59),
    ("Schneller Videoschnitt", "editacademy", 37, 10900, 57),
    ("Ideen für jeden Tag", "ideengarage", 26, 9700, 54),
    ("Call-to-Action Vorlage", "marketingflow", 20, 8800, 52),
    ("Trend-Audio finden", "trendscout", 23, 7900, 49),
    ("Kamera richtig einstellen", "videosetup", 32, 7100, 47),
    ("Bessere Untertitel", "captionwerk", 28, 6400, 44),
    ("Authentisch vor der Kamera", "storywerk", 39, 5800, 41),
    ("Reels mehrfach verwenden", "reelslab", 30, 5200, 38),
    ("Deine Wochenstrategie", "socialplan", 45, 4700, 35),
]

MY_REELS = [
    "5 Content-Ideen für diese Woche", "Warum dein Hook nicht funktioniert",
    "Behind the Scenes: Mein Setup", "Die perfekte Caption schreiben", "Meine Wochenroutine",
    "3 Schnitt-Tricks für Anfänger", "Reichweite ohne Werbung", "Content-Plan für September",
    "Hook in 3 Sekunden", "Mein kompaktes Licht-Setup", "Vorher und nachher: Videoschnitt",
    "So finde ich Trend-Audios", "Mehr Kommentare mit einer Frage", "Untertitel, die gelesen werden",
    "Meine Kamera-Einstellungen", "Storytelling in 30 Sekunden", "Reels mehrfach verwenden",
    "Call to Action ohne Druck", "Drei Ideen gegen Content-Stress", "Meine Wochenstrategie",
]


def seed_demo_data() -> None:
    settings = get_settings()
    if not settings.seed_demo_data:
        return

    with Session(engine) as session:
        reel_count = session.exec(select(func.count()).select_from(Reel)).one()
        if reel_count:
            return

        profiles: dict[str, SocialProfile] = {}
        for handle, name, followers, total_views, engagement in COMPETITORS:
            profile = SocialProfile(
                platform="instagram",
                role="competitor",
                handle=handle,
                display_name=name,
                profile_url=f"https://www.instagram.com/{handle}/",
                followers_count=followers,
                total_views_count=total_views,
                engagement_rate=engagement,
            )
            session.add(profile)
            profiles[handle] = profile

        own_profile = SocialProfile(
            platform="instagram",
            role="own",
            handle="interreels",
            display_name="Inter Reels",
        )
        session.add(own_profile)
        session.flush()

        now = utcnow()
        for index, (title, handle, duration, views, score) in enumerate(TREND_REELS):
            reel = Reel(
                profile_id=profiles[handle].id,
                external_id=f"demo-trend-{index + 1:02d}",
                scope="trending",
                title=title,
                description="So fesselst du deine Zuschauer in den ersten drei Sekunden und führst sie sicher durch deine Story.",
                status="online",
                source_handle=f"@{handle}",
                duration_seconds=duration,
                views_count=views,
                likes_count=max(80, int(views * 0.075)),
                comments_count=max(8, int(views * 0.008)),
                trend_score=score,
                growth_percent=round(score / 20, 1),
                published_at=now - timedelta(hours=index * 5),
            )
            session.add(reel)
            session.flush()
            session.add(
                ReelScript(
                    reel_id=reel.id,
                    hook="Die meisten Reels scheitern an genau diesen drei Fehlern.",
                    body="Starte mit einem starken Hook, zeige sofort den Nutzen und führe dein Publikum Schritt für Schritt durch die Story.",
                    call_to_action="Speichere dieses Reel und teste den Hook bei deinem nächsten Video.",
                    status="ready",
                )
            )

        for index, title in enumerate(MY_REELS):
            is_draft = index % 6 == 0
            is_planned = index % 7 == 3
            status = "draft" if is_draft else "planned" if is_planned else "online"
            views = 0 if status != "online" else max(4700, 42800 - index * 1450)
            reel = Reel(
                profile_id=own_profile.id,
                external_id=f"demo-mine-{index + 1:02d}",
                scope="mine",
                title=title,
                description="Ein eigener Reel-Entwurf aus deiner Content-Bibliothek.",
                status=status,
                source_handle="@interreels",
                duration_seconds=24 + index % 17,
                views_count=views,
                likes_count=int(views * 0.074),
                comments_count=int(views * 0.009),
                trend_score=max(30, 82 - index * 2),
                published_at=now - timedelta(days=index),
            )
            session.add(reel)
            session.flush()
            session.add(
                ReelScript(
                    reel_id=reel.id,
                    hook="Du machst diesen einen Fehler bei deinen Reels.",
                    body="Beginne mit dem Ergebnis, das dein Publikum erreichen möchte, und erkläre danach den Weg.",
                    call_to_action="Speichere den Beitrag für dein nächstes Reel.",
                )
            )

        session.add(AppSetting())
        session.commit()


if __name__ == "__main__":
    seed_demo_data()
