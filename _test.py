from src.backend.core.pipeline import Pipeline, PipelineSpec, PipelineOutput, PipelineConfig, StageContext, Stage
import asyncio


class OcrStageContext(StageContext):
    text: str = ''


class OcrStage(Stage):
    name = 'ocr'
    context_model = OcrStageContext

    async def runnable(self, ctx, prev_ctx=None):
        ctx.text = 'Hi'
        return ctx


class TranslationStageContext(StageContext):
    original_text: str = ''
    translated_text: str = ''


class TranslationStage(Stage):
    name = 'translation'
    context_model = TranslationStageContext

    async def runnable(self, ctx, prev_ctx=None):
        ctx.translated_text = prev_ctx.text
        return ctx


class OcrTranslatePipelineOutput(PipelineOutput):
    text: str = ''
    translated_text: str = ''


class OcrTranslatePipeline(Pipeline):
    spec = PipelineSpec(
        stages=[OcrStage, TranslationStage],
        output_model=OcrTranslatePipelineOutput
    )

    async def handle_output(self, ctxs, output):
        for name, ctx in ctxs.items():
            match name:
                case OcrStage.name:
                    output.text = ctx.text
                case TranslationStage.name:
                    output.translated_text = ctx.translated_text

        return output


if __name__ == '__main__':
    async def main():
        config = PipelineConfig(
            skip_stages=['ocr'],
            force_context_data={
                'ocr': {'text': 'Hi'}
            }
        )
        pipeline = OcrTranslatePipeline()
        output = await pipeline.run(config)
        print(output.model_dump())

    asyncio.run(main())
