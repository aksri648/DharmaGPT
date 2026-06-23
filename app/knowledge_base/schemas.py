from pydantic import BaseModel, Field
from typing import Optional
from app.knowledge_base.constants import SOURCE_BHAGAVAD_GITA


class VerseMetadata(BaseModel):
    source: str = Field(description="Scripture source, e.g. 'Bhagavad Gita'")
    chapter: int
    verse: int
    speaker: Optional[str] = None
    themes: list[str] = Field(default_factory=list)
    emotions: list[str] = Field(default_factory=list)
    character: Optional[str] = None
    category: Optional[str] = None


class Verse(BaseModel):
    text: str
    translation: str
    commentary: Optional[str] = None
    metadata: VerseMetadata


class StoryMetadata(BaseModel):
    title: str
    source: str = Field(description="Source scripture, e.g. 'Ramayana'")
    book: Optional[str] = None
    chapter: Optional[int] = None
    themes: list[str] = Field(default_factory=list)
    emotions: list[str] = Field(default_factory=list)
    characters: list[str] = Field(default_factory=list)
    category: Optional[str] = None


class Story(BaseModel):
    title: str
    summary: str
    teaching: str
    full_text: Optional[str] = None
    metadata: StoryMetadata


class QueryAnalysis(BaseModel):
    emotion: str = Field(description="Primary emotion detected in query")
    theme: str = Field(description="Primary dharma theme relevant to query")
    category: str = Field(description="Life category the query falls under")
    sub_emotions: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class RetrievedVerse(BaseModel):
    text: str
    translation: str
    chapter: int
    verse: int
    source: str = SOURCE_BHAGAVAD_GITA
    speaker: Optional[str] = None
    score: float = 0.0
    themes: list[str] = Field(default_factory=list)


class RetrievedStory(BaseModel):
    title: str
    summary: str
    teaching: str
    source: str = ""
    score: float = 0.0
    themes: list[str] = Field(default_factory=list)


class Context(BaseModel):
    verses: list[RetrievedVerse] = Field(default_factory=list)
    stories: list[RetrievedStory] = Field(default_factory=list)


class Citation(BaseModel):
    source: str
    chapter: Optional[int] = None
    verse: Optional[int] = None
    text: str
    valid: bool = False
