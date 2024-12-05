import logging
from typing import Dict, Generator, Tuple

from src.generator.resume_generator import ResumeGenerator
from src.generator.cover_letter_generator import CoverLetterGenerator
from src.generator.utils.output_manager import OutputManager

logger = logging.getLogger(__name__)

class CombinedGenerator:
    """Handles generation of both resume and cover letter."""
    
    def __init__(self, resume_generator: ResumeGenerator, cover_letter_generator: CoverLetterGenerator):
        self.resume_generator = resume_generator
        self.cover_letter_generator = cover_letter_generator

    def generate_both(self, 
                     job_description: str,
                     selected_sections: Dict[str, str],
                     output_manager: OutputManager):
        """Generate both resume and cover letter in one go."""
        try:
            logger.info("Starting combined resume and cover letter generation")
            # First generate the resume
            resume = None
            logger.debug("Beginning resume generation")
            
            # Track the last result to get the resume object
            last_result = None

            try:
                for result in self.resume_generator.generate_resume(
                    job_description=job_description,
                    selected_sections=selected_sections,
                    output_manager=output_manager
                ):
                    logger.debug(f"Got result type: {type(result)}")
                    if isinstance(result, tuple):
                        status_msg, progress = result
                        logger.debug(f"Progress update: {status_msg} ({progress*100}%)")
                        yield result  # Progress updates
                    else:
                        logger.debug(f"Got non-tuple result: {type(result)}")
                        last_result = result  # Store the final result
                        logger.debug(f"Stored last_result: {type(last_result)}")

                logger.debug(f"Finished resume generation loop, last_result type: {type(last_result)}")
                # Get the resume from the last result
                resume = last_result
                if resume:
                    logger.info(f"Resume generation completed, got resume ID: {resume.id}")
                else:
                    logger.error("Resume is None after generation loop")
                    raise ValueError("Resume generation failed")

                # Then generate the cover letter using the same resume
                logger.info(f"Starting cover letter generation for resume ID: {resume.id}")
                result = self.cover_letter_generator.generate_cover_letter(
                    job_description=job_description,
                    resume_id=resume.id,
                    output_manager=output_manager
                )
                logger.info(f"Cover letter generation result: {result}")

                yield f"Cover letter generation: {result}", 1.0

            except StopIteration:
                logger.error("Resume generator stopped without producing a resume")
                raise ValueError("Resume generation failed prematurely")

        except Exception as e:
            logger.error(f"Failed to generate resume and cover letter: {str(e)}", exc_info=True)
            raise 