from src.models.base_models import Project, ProjectDTO
from uuid import UUID
from typing import List
from src.supabase_tools.supabase_client import SUPABASE_CLIENT
from src.utils.constants import TableNames


async def add_project_to_db(project: Project):
    try:
        print("Adding project to the database")
        print(project)
        print("\n\n")
        serialized_project = project.serialize_for_db()
        response = SUPABASE_CLIENT.table(TableNames.PROJECTS).insert(serialized_project).execute()
        if not response.data:
            raise Exception("Failed to add project to the database")
        return True
    except Exception as e:
        raise Exception(f"An error occurred while adding the project to the database: {e}")
        
async def get_project_from_db(project_id: UUID) -> Project:
    try:
        response = SUPABASE_CLIENT.table(TableNames.PROJECTS).select("*").eq("id", str(project_id)).single().execute()
        project_data = response.data
        if not project_data:
            raise Exception("Project not found")
        return Project(**project_data)
    except Exception as e:
        raise Exception(f"An error occurred while fetching the project from the database: {e}")

async def get_all_projects_from_db(user_id: UUID) -> List[Project]:
    try:
        response = SUPABASE_CLIENT.table(TableNames.PROJECTS).select("*").eq("user_id", str(user_id)).order("created_at", desc=True).execute()
        projects_data = response.data
        if not projects_data:
            raise Exception("No projects found for the given user")
        return [Project(**project) for project in projects_data]
    except Exception as e:
        raise Exception(f"An error occurred while fetching all projects from the database: {e}")
        

async def update_project_in_db(project: Project) -> Project:
    try:
        serialized_project = project.serialize_for_db()
        response = SUPABASE_CLIENT.table(TableNames.PROJECTS).update(serialized_project).eq("id", str(project.id)).execute()
        assert len(response.data) > 0
        if not response.data:
            raise Exception("Failed to update project in the database")
        return True
    except Exception as e:
        raise Exception(f"An error occurred while updating the project in the database: {e}")
        

### 


async def get_project_id_from_prediction_id(prediction_id) -> UUID:
    try:
        response = SUPABASE_CLIENT.table(TableNames.PROJECTS).select("id").eq("lipsync_prediction_id", str(prediction_id)).single().execute()
        if not response.data:
            raise Exception("Prediction not found")
        return UUID(response.data["id"])
    except Exception as e:
        raise Exception(f"An error occurred while fetching the project ID from the prediction ID: {e}")




### 

def project_to_dto(project: Project) -> ProjectDTO:
    return ProjectDTO(
        id=project.id,
        user_id=project.user_id,
        product_id=project.product_id,
        status=project.status,
        video_configuration=project.video_configuration,
        final_script=project.final_script,
        created_at=project.created_at,
        updated_at=project.updated_at,
        final_video_url=project.final_video_url
    )



from uuid import uuid4
from datetime import datetime
from src.models.base_models import Project, ProductBase, ProjectStatus, Asset, VideoConfiguration, Script, ActorBase, VoiceBase, VideoLayoutBase


async def get_dummy_project():
    # Constructing the ProductBase object
    product_base = ProductBase(
        name="Sample Product",
        description="This is a sample product",
        product_link="https://example.com",
        logo_url="https://example.com/logo.png",
        thumbnail_url="https://example.com/thumbnail.png"
    )

    # Constructing the VideoConfiguration object
    video_configuration = VideoConfiguration(
        duration=30,
        target_audience="General Audience",
        cta="Visit our website",
        direction="Top to bottom"
    )

    # Constructing the Script object
    script = Script(
        id=uuid4(),
        title="Sample Script",
        content="This is the content of the sample script."
    )

    # Constructing the ActorBase object
    actor_base = ActorBase(
        name="Sample Actor",
        gender="Male",
        full_video_link="https://example.com/actor_video.mp4",
        thumbnail_image_url="https://example.com/actor_thumbnail.png",
        default_voice_id=uuid4()
    )

    # Constructing the VoiceBase object
    voice_base = VoiceBase(
        name="Sample Voice",
        gender="Male",
        voice_identifier="alloy"
    )

    # Constructing the VideoLayoutBase object
    video_layout_base = VideoLayoutBase(
        name="Sample Layout",
        description="This is a sample layout",
        thumbnail_url="https://example.com/layout_thumbnail.png"
    )

    # Constructing the Project object
    project = Project(
        id=uuid4(),
        product_id=UUID("12345678-1234-5678-1234-567812345678"),
        user_id=UUID("71b4a027-290b-4aaf-988b-1e789504c0ac"),
        product_base=product_base,
        status=ProjectStatus.CREATED,
        assets=[
            Asset(type="image", url="https://example.com/asset1.png"),
            Asset(type="video", url="https://example.com/asset2.mp4")
        ],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        final_script="This is the final script.",
        video_configuration=video_configuration,
        script=script,
        actor_id=UUID("4e4a6cc7-f044-4445-9548-f0933b0cbe0e"),
        actor_base=actor_base,
        voice_id=UUID("a059382e-5d8d-49ec-96d1-eb7e46c04e31"),
        voice_base=voice_base,
        video_layout_id=UUID("fc9ce3d6-5133-4dde-b347-9b030b773517"),
        video_layout_base=video_layout_base,
        t2s_audio_url="https://example.com/t2s_audio.mp3",
        lipsync_prediction_id="sample_prediction_id",
        lipsync_video_url="https://example.com/lipsync_video.mp4",
        final_video_duration=60.0,
        final_video_url="https://example.com/final_video.mp4"
    )

    return project

async def main():
    project = await get_dummy_project()
    project.id = UUID("84322c61-8cb2-411f-a9b5-32a9947a5ea5")
    project.status = ProjectStatus.TEST
    project.t2s_audio_url = "https://example.com/kc_new_t2s_audio.mp3"
    # Adding the project to the database
    await update_project_in_db(project)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())